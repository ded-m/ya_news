import pytest
from django.urls import reverse
from http import HTTPStatus
from news.models import Comment
# Импортируем функции для проверки редиректа и ошибки формы:
from pytest_django.asserts import assertRedirects, assertFormError
# Импортируем из модуля forms сообщение об ошибке:
from news.forms import BAD_WORDS, WARNING

COMMENT_TEXT = 'Текст комментария'
NEW_COMMENT_TEXT = 'Обновлённый комментарий'


def test_anonymous_user_cant_create_comment(author, client, detail_url, news):
    # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
    # предварительно подготовленные данные формы с текстом комментария.
    comments_count_before = Comment.objects.count()  
    client.post(detail_url, data={'text': COMMENT_TEXT})
    # Считаем количество комментариев.
    comments_count_after = Comment.objects.count()
    # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
    assert comments_count_after - comments_count_before == 0


def test_user_can_create_comment(author, author_client, detail_url, news):
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data={'text': COMMENT_TEXT})
    # Проверяем, что редирект привёл к разделу с комментами.
    assertRedirects(response, f'{detail_url}#comments')
    # Считаем количество комментариев.
    comments_count_after = Comment.objects.count()
    # Убеждаемся, что добавлен один комментарий.
    assert comments_count_after - comments_count_before == 1
    # Получаем объект добавленного комментария из базы.
    comment = Comment.objects.last()
    # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
    assert comment.text == COMMENT_TEXT
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, detail_url):
    comments_count_before = Comment.objects.count()
    # Формируем данные для отправки формы; текст включает
    # первое слово из списка стоп-слов.
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    # Отправляем запрос через авторизованный клиент.
    response = author_client.post(detail_url, data=bad_words_data)
    # Проверяем, есть ли в ответе ошибка формы.
    assertFormError(
            response,
            form='form',
            field='text',
            errors=WARNING
        )
    comments_count_after = Comment.objects.count()
    # Дополнительно убедимся, что комментарий не был создан.
    assert comments_count_after - comments_count_before == 0


def test_author_can_delete_comment(author_client, detail_url):
    comments_count_before = Comment.objects.count()
    comment = Comment.objects.last()
    # URL для удаления комментария.
    delete_url = reverse('news:delete', args=(comment.id,))
    # От имени автора комментария отправляем DELETE-запрос на удаление.
    response = author_client.delete(delete_url)
    # Проверяем, что редирект привёл к разделу с комментариями.
    # Заодно проверим статус-коды ответов.
    assertRedirects(response, f'{detail_url}#comments')
    # Считаем количество комментариев в системе.
    comments_count_after = Comment.objects.count()
    # Ожидаем уменьшение количества комментариев в системе на 1.
    assert comments_count_after - comments_count_before == -1


def test_user_cant_delete_comment_of_another_user(reader_client, detail_url):
    comments_count_before = Comment.objects.count()
    comment = Comment.objects.last()
    # URL для удаления комментария.
    delete_url = reverse('news:delete', args=(comment.id,))
    # Выполняем запрос на удаление от пользователя-читателя.
    response = reader_client.delete(delete_url)
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Считаем количество комментариев в системе.
    comments_count_after = Comment.objects.count()
    # Ожидаем, что количество комментариев не уменьшилось.
    assert comments_count_after - comments_count_before == 0


def test_author_can_edit_comment(author_client, detail_url):
    comment = Comment.objects.last()
    # URL для редактирования комментария.
    edit_url = reverse('news:edit', args=(comment.id,))
    # От имени автора комментария отправляем EDIT-запрос на редактирование.
    response = author_client.post(edit_url, data={'text': NEW_COMMENT_TEXT})
    # Проверяем, что редирект привёл к разделу с комментариями.
    assertRedirects(response, f'{detail_url}#comments')
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст комментария соответствует обновленному.
    assert comment.text == NEW_COMMENT_TEXT


def test_user_cant_edit_comment_of_another_user(reader_client, detail_url):
    comment = Comment.objects.last()
    # URL для редактирования комментария.
    edit_url = reverse('news:edit', args=(comment.id,))
    # От имени читателя отправляем EDIT-запрос на редактирование.
    response = reader_client.post(edit_url, data={'text': NEW_COMMENT_TEXT})
    # Проверяем, что вернулась 404 ошибка.
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Обновляем объект комментария.
    comment.refresh_from_db()
    # Проверяем, что текст остался тем же, что и был.
    assert comment.text == COMMENT_TEXT
