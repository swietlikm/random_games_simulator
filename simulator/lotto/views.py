import json

from celery import states
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Case, DecimalField, Value, When
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, RedirectView, TemplateView, UpdateView
from django_celery_results.models import TaskResult

from .forms import LottoGameUpdateForm, NewLottoGameForm, RandomLottoForm
from .models import LottoCoupon, LottoGame
from .tasks import bulk_create_coupons, bulk_update_coupons_status


class LottoHomePageView(LoginRequiredMixin, TemplateView):
    template_name = "pages/lotto_games.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        task_running = TaskResult.objects.filter(status=states.STARTED).first()
        games = LottoGame.objects.all()

        if task_running:
            task_data = json.loads(task_running.result)
            games = games.annotate(
                task_progress=Case(
                    When(id=task_data.get("game_id"), then=task_data.get("progress")),
                    default=Value(None),
                    output_field=DecimalField(),
                ),
            )

        open_games = games.filter(status="OPEN")
        context["open_games"] = open_games

        closed_games = games.filter(status="CLOSED")
        context["closed_games"] = closed_games

        return context


class LottoGameCreateView(LoginRequiredMixin, CreateView):
    template_name = "pages/form.html"
    model = LottoGame
    form_class = NewLottoGameForm
    success_url = reverse_lazy("lotto:index")
    extra_context = {"text": "Create new game"}


class LottoGameUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "pages/form.html"
    model = LottoGame
    form_class = LottoGameUpdateForm
    success_url = reverse_lazy("lotto:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["text"] = str(self.get_object()) + " - Update"
        context["coupons"] = self.object.lottocoupons.count()
        return context

    def form_valid(self, form):
        game = self.object

        if form.cleaned_data.get("numbers"):
            game.numbers = form.cleaned_data["numbers"]

        if game.numbers and len(game.numbers) == 6:
            game.status = "CLOSED"
            game.save()

            bulk_update_coupons_status.delay(game.id)  # perform coupons evaluation in the background (Celery)

        return super().form_valid(form)


class LottoGameDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "pages/form.html"
    model = LottoGame
    success_url = reverse_lazy("lotto:index")
    extra_context = {"text": "Are you sure to delete this game?", "btn_color": "btn-danger", "btn_name": "Delete"}


class LottoGameDetailsView(LoginRequiredMixin, ListView):
    template_name = "pages/lotto_game_details.html"
    context_object_name = "lotto_coupons"
    paginate_by = 100

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return LottoCoupon.objects.filter(game_id=pk, user=self.request.user).order_by("-status")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["game"] = queryset.first().game
        context["total_coupons"] = queryset.count()
        context["chance"] = round((context["total_coupons"] / 13983816) * 100, 2)
        context["hit_6"] = queryset.filter(status="6").count()
        context["hit_6_prc"] = round((context["hit_6"] / context["total_coupons"]) * 100, 2)
        context["hit_6_prize"] = context["hit_6"] * 15000000
        context["hit_5"] = queryset.filter(status="5").count()
        context["hit_5_prc"] = round((context["hit_5"] / context["total_coupons"]) * 100, 2)
        context["hit_5_prize"] = context["hit_5"] * 5000
        context["hit_4"] = queryset.filter(status="4").count()
        context["hit_4_prc"] = round((context["hit_4"] / context["total_coupons"]) * 100, 2)
        context["hit_4_prize"] = context["hit_4"] * 100
        context["hit_3"] = queryset.filter(status="3").count()
        context["hit_3_prize"] = context["hit_3"] * 20
        context["hit_3_prc"] = round((context["hit_3"] / context["total_coupons"]) * 100, 2)
        context["hit_2"] = queryset.filter(status="2").count()
        context["hit_2_prc"] = round((context["hit_2"] / context["total_coupons"]) * 100, 2)
        context["hit_2_prize"] = 0
        context["hit_1"] = queryset.filter(status="1").count()
        context["hit_1_prc"] = round((context["hit_1"] / context["total_coupons"]) * 100, 2)
        context["hit_1_prize"] = 0
        context["hit_0"] = queryset.filter(status="0").count()
        context["hit_0_prc"] = round((context["hit_0"] / context["total_coupons"]) * 100, 2)
        context["hit_0_prize"] = 0
        context["total_prize"] = (
            context["hit_6_prize"] + context["hit_5_prize"] + context["hit_4_prize"] + context["hit_3_prize"]
        )

        paginator = Paginator(context["lotto_coupons"], self.paginate_by)

        page = self.request.GET.get("page", 1)

        try:
            lotto_coupons = paginator.page(page)
        except PageNotAnInteger:
            lotto_coupons = paginator.page(1)
        except EmptyPage:
            lotto_coupons = paginator.page(paginator.num_pages)

        context["lotto_coupons"] = lotto_coupons
        return context


class GenerateLottoCouponsView(LoginRequiredMixin, FormView):
    template_name = "pages/form.html"
    form_class = RandomLottoForm
    success_url = reverse_lazy("lotto:index")
    extra_context = {"text": "Add coupons"}

    def form_valid(self, form):
        game_id = self.kwargs["pk"]
        cleaned_data = form.cleaned_data
        quantity = cleaned_data["quantity"]

        bulk_create_coupons.delay(self.request.user.id, game_id, quantity)
        if quantity > 1000:
            messages.info(
                self.request,
                "Coupons are being generated in the background. Please wait until all coupons are generated",
            )
        return HttpResponseRedirect(self.get_success_url())


class RemoveCouponsView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        game_id = self.kwargs["pk"]
        LottoGame.objects.get(pk=game_id).lottocoupons.filter(user=self.request.user).delete()

        return reverse("lotto:index")
