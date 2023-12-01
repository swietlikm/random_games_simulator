import random
import time

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, FormView, ListView, RedirectView, TemplateView, UpdateView

from .forms import RandomLottoForm
from .models import LottoGame, UserNumbers


def generate_random_numbers():
    return random.sample(range(1, 50), 6)


class LottoHomePageView(LoginRequiredMixin, TemplateView):
    template_name = "pages/lotto_games.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        open_games = LottoGame.objects.filter(status="OPEN")
        context["open_games"] = open_games

        closed_games = LottoGame.objects.filter(status="CLOSED")
        context["closed_games"] = closed_games
        return context


class LottoGameDetailsView(LoginRequiredMixin, ListView):
    template_name = "pages/lotto_game_details.html"
    context_object_name = "user_numbers"
    paginate_by = 100

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return UserNumbers.objects.filter(game_id=pk).order_by("-status")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context["total_coupons"] = queryset.count()
        context["hit_6"] = queryset.filter(status="6").count()
        context["hit_5"] = queryset.filter(status="5").count()
        context["hit_4"] = queryset.filter(status="4").count()
        context["hit_3"] = queryset.filter(status="3").count()
        context["hit_2"] = queryset.filter(status="2").count()
        context["hit_1"] = queryset.filter(status="1").count()
        context["hit_0"] = queryset.filter(status="0").count()

        paginator = Paginator(context["user_numbers"], self.paginate_by)
        page = self.request.GET.get("page")

        try:
            user_numbers = paginator.page(page)
        except PageNotAnInteger:
            user_numbers = paginator.page(1)
        except EmptyPage:
            user_numbers = paginator.page(paginator.num_pages)

        context["user_numbers"] = user_numbers
        return context


class RandomLottoView(LoginRequiredMixin, FormView):
    template_name = "pages/form.html"
    form_class = RandomLottoForm
    success_url = reverse_lazy("lotto:index")
    extra_context = {"text": "Add coupons"}

    # def form_valid(self, form):
    #     start_time = time.time()
    #
    #     game_id = self.kwargs['pk']
    #     cleaned_data = form.cleaned_data
    #     quantity = cleaned_data['quantity']
    #
    #     user_numbers_list = []
    #     for _ in range(quantity):
    #         user_numbers_list.append(UserNumbers(
    #             user=self.request.user,
    #             game_id=game_id,
    #             numbers=generate_random_numbers(),
    #         ))
    #
    #     with transaction.atomic():
    #         UserNumbers.objects.bulk_create(user_numbers_list)
    #
    #     end_time = time.time()
    #     execution_time = end_time - start_time
    #     print(f"Transaction execution Time: {execution_time} seconds")
    #
    #     messages.success(self.request, f'Successfully added {quantity} coupons to Game {game_id}')
    #     return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        start_time = time.time()

        game_id = self.kwargs["pk"]
        cleaned_data = form.cleaned_data
        quantity = cleaned_data["quantity"]
        batch_size = 500  # Set your desired batch size

        for offset in range(0, quantity, batch_size):
            user_numbers_list = []
            end_index = min(offset + batch_size, quantity)

            for _ in range(offset, end_index):
                user_numbers_list.append(
                    UserNumbers(
                        user=self.request.user,
                        game_id=game_id,
                        numbers=generate_random_numbers(),
                    )
                )

            with transaction.atomic():
                UserNumbers.objects.bulk_create(user_numbers_list)

            # Sleep for a short time to avoid overloading the system
            time.sleep(0.05)

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Transaction execution Time: {execution_time} seconds")

        messages.success(self.request, f"Successfully added {quantity} coupons to Game {game_id}")
        return HttpResponseRedirect(self.get_success_url())


class ClearUserNumbersView(RedirectView):
    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        game_id = self.kwargs["pk"]

        LottoGame.objects.get(pk=game_id).usernumbers.filter(user=self.request.user).delete()

        return reverse("lotto:index")


class LottoGameCreateView(LoginRequiredMixin, CreateView):
    template_name = "pages/form.html"
    model = LottoGame
    fields = ("date",)
    success_url = reverse_lazy("lotto:index")
    extra_context = {"text": "Create new game"}


class LottoGameUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "pages/form.html"
    model = LottoGame
    fields = "__all__"
    # fields = ('date', 'numbers')
    success_url = reverse_lazy("lotto:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["text"] = str(self.get_object()) + " - Update"
        context["coupons"] = self.object.usernumbers.count()
        return context


class LottoGameDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "pages/form.html"
    model = LottoGame
    success_url = reverse_lazy("lotto:index")
    extra_context = {"text": "Are you sure to delete this game?", "btn_color": "btn-danger", "btn_name": "Delete"}
