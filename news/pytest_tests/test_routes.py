from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.parametrize(
    'name, args',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
@pytest.mark.django_db
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name, args):
    if args is not None:
        url = reverse(name, args=(args.id,))  # Получаем ссылку на нужный адрес.
    else:
        url = reverse(name)

    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user_client, status',
    (
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    )
)
def test_availability_for_comment_edit_and_delete(user_client, status, name, args):
    url = reverse(name, args=(args.id,))
    response = user_client.get(url)
    assert response.status_code == status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment')),
        ('news:delete', pytest.lazy_fixture('comment')),
    )
)
def test_redirect_for_anonymous_client(client, name, args):
    # Сохраняем адрес страницы логина:
    login_url = reverse('users:login')
    url = reverse(name, args=(args.id,))
    # Получаем ожидаемый адрес страницы логина, 
    # на который будет перенаправлен пользователь.
    # Учитываем, что в адресе будет параметр next, в котором передаётся
    # адрес страницы, с которой пользователь был переадресован.
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    # Проверяем, что редирект приведёт именно на указанную ссылку.
    assertRedirects(response, redirect_url)
