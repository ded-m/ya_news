import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from news.models import News, Comment
from django.urls import reverse


@pytest.fixture
# Используем встроенную фикстуру для модели пользователей django_user_model.
def author(django_user_model):
    return django_user_model.objects.create(username='Лев Толстой')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Читатель простой')


@pytest.fixture
def news():
    news = News.objects.create(  # Создаём объект новости.
        title='Заголовок',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(  # Создаём объект комментария.
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client


@pytest.fixture
def reader_client(reader, client):  # Вызываем фикстуру читателя и клиента.
    client.force_login(reader)  # Логиним читателя в клиенте.
    return client


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
                title=f'Новость {index}',
                text='Просто текст.',
                # Для каждой новости уменьшаем дату на index дней от today,
                # где index - счётчик цикла.
                date=today - timedelta(days=index)
            )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
    News.objects.bulk_create(all_news)
    return all_news


@pytest.fixture
def detail_url(news, author):
    # Сохраняем в переменную адрес страницы с новостью:
    detail_url = reverse('news:detail', args=(news.id,))
    # Запоминаем текущее время:
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(2):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(  # Создаём объект комментария.
            news=news,
            text='Текст комментария',
            author=author,
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()
    return detail_url
