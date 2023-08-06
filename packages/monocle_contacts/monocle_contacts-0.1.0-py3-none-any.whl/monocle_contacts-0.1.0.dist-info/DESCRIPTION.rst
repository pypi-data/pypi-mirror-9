monocle_contacts app
==================

Модуль: monocle_contacts

#. Структура папок модуля
#. Конфигурационный файл
#. json файл импорта
#. Публикация через pip3
#. Внесение изменений в модули


**Структура папок модуля**

Модуль представляет собой стандартное приложение для django и включает в себя модели, средства генерации систем управления, шаблоны, статические файлы, а также файлы для интеграции и сборки.
Так как модуль встраивается в одностраничный сайт с помощью сборщика, то у него нет файлов view.py и urls.py. Для передачи данных из модуля в основной проект используется файл mionocle.py содеражащий нужные вызовы для определенного модуля.
Модули являются частями проекта автоматической сборки одностраничных сайтов на django - https://bitbucket.org/langprism/django-monocle.
Необходимо соблюдать следующие условия наименования файлов и папок.

* monocle_
    * templates
        * monocle_
            *monocle_.html
    * static
        * monocle_
            * assets
            * monocle_.css
            * monocle_.js
    * fixtures
        *monocle_
            [Картинки]
        *monocle_,json
    * models.py
    * admin.py
    * monocle.py
* MANIFEST.in
* README.rst
* setup.py
* reqs.txt

**Конфигурационный файл**

Для сборки и интеграции проекта сборщик django-monocle использует файл модуля monocle.py: ::


    # название модуля - должно совпадать с 
    appname = 'monocle_sample'

    # модели импортируемые в основное приложение одностраничного проекта
    models = ['SampleModel']

    """
        строка передающая данные из модели в контекст основного шаблона. Этот вызов используется во view.py файле основого приложения проекта при сборке.
    """
    context_callback =  "'monocle_sample_models': SampleModel.objects.all().filter(isShown=True)"

   included_app_reqs = [ ] - зависимости, подключаемые в файле settings.py проекта.

**json файл импорта**
Пример: ::

    [
    {
     "model": "monocle_partners.partner",
     "fields": {
      "position": 0,
      "image": "monocle_partners/image.jpg",
      "name": "Партнер1",
      "isShown": true
     },
     "pk": 1
    },
    {
     "model": "monocle_partners.partner",
     "fields": {
      "position": 2,
      "image": "monocle_partners/image.jpg",
      "name": "Партнер2",
      "isShown": true
     },
     "pk": 2
    }
    ]

**Публикация через pip3**

Модули устанавливаются сборщиком при помощи менеджера пакетов pip3. Поэтому после внесения изменений в модуль необходимо собрать его в дистрибутив и опубликовать в pipy.
Для этого нужно отредактировать файл setup.py: ::

    setup(
        name='',
        version='0.1.0',
        packages=[''],
        include_package_data=True,
        install_requires=[
        "requests",
        "bcrypt",
        ],
        license='BSD License',  # example license
        description='Sample app for django-monocle project',
        long_description=README,
        author='Alexander Kalinin @Langprism LTD',
        author_email='ak@langprism.com',
        classifiers=[
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License', # example license
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            # Replace these appropriately if you are stuck on Python 2.
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Topic :: Internet :: WWW/HTTP',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
    )

Зависимости пакетов указываются в файле setup.py в атрибуте "install_requires" (см. пример выше).

После редактирования нужно выполнить команду: ::

    python3 setup.py register sdist bdist_wheel upload

Для публикации дистрибутива в индексе нужно ввести данные аккаунта проекта:
логин - monoculus,
пароль - Langprism11

**Внесение изменений в модули**

В случае если модуль необходимо доработать либо внести изменения, необходимо склонировать его с репозитория. Хранилище модулей находится по ссылке https://bitbucket.org/monoculus.
После изменений необходимо снова опубликовать проект pypi, инкрементировать номер версии и выполнить push в репозиторий.

