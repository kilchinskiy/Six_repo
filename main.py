  #Modul 8 Home work 1

from collections import UserDict  # Імпортуємо класс словаря AddressBook.
from datetime import datetime, timedelta  # Робота с датами.
import pickle  # Для серіалізації/десеріалізації


class Field:  # Базові класи. Зберігання значень.
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):  # Базові класи. Збергігання імен.
    pass


class Phone(Field):  # Базові класи. Робить перевірку телефону.
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone must contain 10 digits.")
        super().__init__(value)


class Birthday(Field):  # Базові класи. Дата народження.
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)


class Record:  # Зберігає данні.
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):  # Додати телефон.
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):  # Видалити телефон.
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        """
        Исправленный метод:
        1) Находим индекс старого номера.
        2) Валидируем новый номер (создание Phone(new_phone) -> может бросить ValueError).
        3) Если валидно — заменяем по индексу.
        4) Если старый номер не найден — бросаем ValueError("Phone not found.")
        """
        idx = None
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                idx = i
                break

        if idx is None:
            raise ValueError("Phone not found.")

        # Валидируем новый номер до изменения списка:
        new_phone_obj = Phone(new_phone)  # может поднять ValueError("Phone must contain 10 digits.")
        # Только после успешной валидации — произвести замену:
        self.phones[idx] = new_phone_obj
        return

    def find_phone(self, phone):  # Знайти телефон.
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):  # Додати дату народження.
        self.birthday = Birthday(birthday)

    def __str__(self):  # Відображення строк.
        phones = "; ".join(p.value for p in self.phones) if self.phones else "No phones"
        birthday = self.birthday.value if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"


class AddressBook(UserDict):  # Адресна книга.
    def add_record(self, record):  # Додати новий контакт.
        self.data[record.name.value] = record

    def find(self, name):  # Знайти контакт за ім'ям.
        return self.data.get(name)

    def delete(self, name):  # Видалити контакт.
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):  # Знайти усіх ДР за 7 днів.
        today = datetime.today().date()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday.replace(year=today.year)
                if bday_this_year < today:  # Якщо ДР був, перенос на наступний рік.
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                delta = (bday_this_year - today).days
                if 0 <= delta <= 7:
                    congrats_day = bday_this_year
                    if congrats_day.weekday() >= 5:  # Перенос на понеділок, якщо ДР на вихідних.
                        congrats_day += timedelta(days=(7 - congrats_day.weekday()))
                    upcoming.append({
                        "name": record.name.value,
                        "birthday": congrats_day.strftime("%d.%m.%Y")
                    })
        return upcoming

    def __str__(self):  # Вивід усіх контактів.
        return "\n".join(str(record) for record in self.data.values())


# Функции сохранения/загрузки
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:  # Невірний формат або Phone not found
            return str(e)
        except KeyError:  # Немає контакту
            return "Contact not found."
        except IndexError:  # Немає аргументів.
            return "Enter the argument for the command."
        except Exception as e:
            return f"Error: {e}"
    return inner


@input_error
def add_contact(args, book: AddressBook):  # Додати новий контакт чи телефон до існуючого.
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        # edit_phone теперь валидирует новый номер до замены
        record.edit_phone(old_phone, new_phone)
        return "Phone updated."
    else:
        raise KeyError


@input_error
def show_phone(args, book: AddressBook): # Відобразити телефони контакта.
    name, *_ = args
    record = book.find(name)
    if record:
        return "; ".join(p.value for p in record.phones) or "No phones"
    else:
        return "Contact not found."


@input_error
def show_all(book: AddressBook): # Вивід контактів.
    if not book.data:
        return "No contacts found."
    return str(book)


@input_error
def add_birthday(args, book: AddressBook): # Додати ДР контакту.
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError


@input_error
def show_birthday(args, book: AddressBook): # Відобразити день народження.
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday.value}"
    elif record:
        return f"{name} has no birthday set."
    else:
        raise KeyError


@input_error
def birthdays(args, book: AddressBook): # Відобразити ДР на тиждень.
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays."
    return "\n".join(f"{item['name']}: {item['birthday']}" for item in upcoming)


def parse_input(user_input): # Парсер команд.
    if not user_input or not user_input.strip():
        return "", []
    parts = user_input.split()
    cmd = parts[0].strip().lower()
    args = parts[1:]
    return cmd, args


def main():
    book = load_data()  # загружаем при старте (если есть файл)
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command == "":
            print("You entered nothing. Try again.")
            continue

        if command in ["close", "exit"]:
            save_data(book)  # сохраняем перед выходом
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()