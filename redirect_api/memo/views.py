from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from django.urls import reverse_lazy
from .models import Memo
from .forms import MemoForm
from django.shortcuts import get_object_or_404


class MemoListView(LoginRequiredMixin, ListView):
    model = Memo
    context_object_name = 'memos'
    template_name = 'memos/memo_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        memo_pk = self.kwargs.get('pk')
        if memo_pk:
            context['selected_memo'] = get_object_or_404(Memo, pk=memo_pk, user=self.request.user)
        return context
    
class MemoUpdateView(LoginRequiredMixin, UpdateView):
    model = Memo
    form_class = MemoForm
    template_name = 'memos/memo_form.html'

    def get_queryset(self):
        # ログインユーザーのメモのみを更新可能にする
        return Memo.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('memo:memo_list', kwargs={'pk': self.object.pk})

class MemoDeleteView(LoginRequiredMixin, DeleteView):
    model = Memo
    template_name = 'memos/memo_confirm_delete.html'

    def get_queryset(self):
        # ログインユーザーのメモのみを削除可能にする
        return Memo.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('memo:memo_list')

class MemoCreateView(LoginRequiredMixin, CreateView):
    model = Memo
    form_class = MemoForm
    template_name = 'memos/memo_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user  # メモを作成するユーザーを設定
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('memo:memo_list', kwargs={'pk': self.object.pk}) # メモ作成後にメモ一覧ページへリダイレクト
