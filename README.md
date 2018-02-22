# liker-group-script

Likes people from groups VK

Ставит лайки людям из групп ВКонтакте

## Instruction
1. Install all requirements:  
`pip3 install -r requirements.txt`

2. **You should firstly run** `configure.py` in order to create **.cfg** files:  
`python3 configure.py`

3. Now you can run script, enjoy new followers and friends:  
`python3 main.py`

## Инструкция:
1. Установите зависимости:  
`pip3 install -r requirements.txt`

2. **Сперва запустите конфигуратор** `configure.py` чтобы создать **.cfg** файлы:  
`python3 configure.py`

3. Запустите скрипт:  
`python3 main.py`

## Information
This Python 3 script has separate class `WorkInformation` containing all information about work and allowing to configure your **.cfg** files. `main.py` does all the work - gets all users from group members and put likes every 3 posts on their page. Program prints all middle results, can handle captcha and catches the majority of `Exceptions`. For requests to VkAPI I use this lib - https://github.com/dimka665/vk

## Информация
Этот скрипт, написанный на Python 3 содержит отдельный класс `WorkInformation` со всей информацией по работе и позволяющий настроить файлы конфигов. `main.py` делает всю работу. Программы выводит в консоль промежуточые результаты, умеет обрабатывать капчу и оповещает о большинстве `Exception`. Для запросов используется библиотека из репозитория https://github.com/dimka665/vk
