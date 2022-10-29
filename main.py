import requests
import datetime
import time
import os


users_dict = requests.get('https://json.medrocket.ru/users').json()
tasks_dict = requests.get('https://json.medrocket.ru/todos').json()


def main():
    '''
    Основная функция в которой:
    1. Берём из ссылок информацию и вносим их в переменные
    2. Делаем проверку длины задач, чтобы не превышало 46 элементов
    3. Ведём подсчет Актуальных и Завершённых задач
    4. Перед каждой строчкой задач обязательно вставляем "-"
    5. Проверяем на различные исключения
    '''
    for user in users_dict:
        company = user['company']['name']
        current_time = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        content = f"# Отчет для {company}.\n"
        content += f"{user['name']} <{user['email']}> {current_time} \n"
        tasks = 0
        finished_task = ''
        unfinished_tasks = ''
        try:
            for task in tasks_dict:
                if len(task['title']) > 46:
                    task['title'] = task['title'][:46] + '...'
                if user['id'] == task['userId']:
                    tasks += 1
                    if task['completed']:
                        finished_task += '- ' + task['title'] + '\n'
                    else:
                        unfinished_tasks += '- ' + task['title'] + '\n'
        except KeyError:
            finish = finished_task.count('\n')
            unfinish = unfinished_tasks.count('\n')
            if tasks == 0:
                content += 'У пользователя нет задач'
            else:
                content += f'Всего задач: {tasks} \n \n'
                content += f'## Актуальные задачи ({unfinish}): \n'
                content += unfinished_tasks + '\n'
                content += f'## Завершённые задачи ({finish}): \n'
                content += finished_task
                create_report(user['username'], content)
        except requests.exceptions.HTTPError as http_error:
            print("HTTP Error:", http_error)
        except requests.exceptions.ConnectionError as connection_error:
            print("Connection Error:", connection_error)
        except requests.exceptions.Timeout as timeour_error:
            print("Timeout Error:", timeour_error)
        except requests.exceptions.RequestException as request_error:
            print("Request Error:", request_error)
    get_fail()

def create_report(file_name, content):
    '''
    Функция принимает значения content
    по полученным данным формируется
    и возвращается отчёт
    '''
    if os.path.exists(f'tasks/{file_name}.txt'):
        change_file_name(file_name)
    if not os.path.isdir("tasks"):
        os.mkdir("tasks")
    file = open(f"tasks/{file_name}.txt", "x", encoding="UTF-8")
    file.write(content)
    file.close()

def get_fail():
    '''
    Создаём файл с пустыми задачами
    которые имею id
    но наполнение отсутствует
    '''
    content = ''
    for task in tasks_dict:
        if 'userId' not in task:
            content += 'Отсутствует задание номер: ' + str(task['id']) + '\n'
    create_report('Некорректные задачи', content)

def change_file_name(file_name):
    '''
    Функция, которая переименовывает в папке "tasks"
    файл структуры "Name.txt"
    на "old_Name_2020-09-23T15:25.txt"
    '''
    creation_time = time.localtime(os.path.getmtime(f"tasks/{file_name}.txt"))
    title_time = time.strftime('%Y-%m-%dT%H.%M', creation_time)
    return os.rename(f"tasks/{file_name}.txt", f"tasks/old_{file_name}_{title_time}.txt")


if __name__ == "__main__":
    main()
