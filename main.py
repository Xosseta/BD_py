import psycopg2
from pprint import pprint


def create_db(conn):
    conn.execute("""
            create table if not exists client(
                id serial primary key,
                name varchar(20),
                surname varchar(20),
                email varchar(200)
            );
            """)
    conn.execute("""
            create table if not exists numbers(
                number varchar(11) primary key,
                client_id integer references client(id)
            );         
            """)
    return


def add_phone(conn, client_id, number):
    conn.execute("""
            insert into numbers(number, client_id)
            values(%s, %s)
            """, (number, client_id))
    return client_id


def delete_db(conn):
    conn.execute("""
        DROP TABLE client, numbers CASCADE;
        """)


def add_client(conn, name, surname, email, number=None):
    conn.execute("""
            insert into client(name, surname, email)
            values(%s, %s, %s)        
            """, (name, surname, email))
    conn.execute("""
            select id from client
            order by id desc
            limit 1
            """)
    id = conn.fetchone()[0]
    if number is None:
        return id
    else:
        add_phone(conn, id, number)
        return id


def change_client(conn, client_id, name=None, surname=None, email=None):
    conn.execute("""
            select * from client
            where id = %s
            """, (client_id, ))
    info = conn.fetchone()
    if name is None:
        name = info[1]
    if surname is None:
        surname = info[2]
    if email is None:
        email = info[3]
    conn.execute("""
            update client
            set name = %s, surname = %s, email = %s
            where id = %s
            """, (name, surname, email, client_id))
    return id


def delete_number(conn, number):
    conn.execute("""
            delete from numbers
            where number = %s
            """, (number, ))
    return number


def delete_client(conn, id):
    conn.execute("""
            delete from numbers
            where client_id = %s
            """, (id, ))
    conn.execute("""
            delete from client
            where id = %s
            """, (id, ))
    return id


def find_client(conn, name=None, surname=None, email=None, tel=None):
    if name is None:
        name = '%'
    else:
        name = '%' + name + '%'
    if surname is None:
        surname = '%'
    else:
        surname = '%' + surname + '%'
    if email is None:
        email = '%'
    else:
        email = '%' + email + '%'
    if tel is None:
        conn.execute("""
                SELECT c.id, c.name, c.surname, c.email, n.number FROM client c
                LEFT JOIN numbers n ON c.id = n.client_id
                WHERE c.name LIKE %s AND c.surname LIKE %s
                AND c.email LIKE %s
                """, (name, surname, email))
    else:
        conn.execute("""
                SELECT c.id, c.name, c.surname, c.email, n.number FROM client c
                LEFT JOIN numbers n ON c.id = n.client_id
                WHERE c.name LIKE %s AND c.surname LIKE %s
                AND c.email LIKE %s AND n.number like %s
                """, (name, surname, email, tel))
    return conn.fetchall()


with psycopg2.connect(database="netology_db", user="postgres", password="Vladik1999") as conn:
    with conn.cursor() as cur:
        delete_db(cur)
        create_db(cur)
        print("БД создана")
        print("Добавлен клиент id: ",
              add_client(cur, "Николай", "Постнов", "3218K@gmail.com"))
        print("Добавлен клиент id: ",
              add_client(cur, "Екатерина", "Шмонькина",
                            "KATY21@mail.ru", 79895424635))
        print("Добавлен клиент id: ",
              add_client(cur, "Игорь", "Селезнёв",
                            "fort@outlook.com", 79354932457))
        print("Данные в таблицах")
        cur.execute("""
                        SELECT c.id, c.name, c.surname, c.email, n.number FROM client c
                        LEFT JOIN numbers n ON c.id = n.client_id
                        ORDER by c.id
                        """)
        pprint(cur.fetchall())
        print("Телефон добавлен клиенту id: ",
              add_phone(cur, 3, 79852146215))
        print("Телефон добавлен клиенту id: ",
              add_phone(cur, 1, 79625478235))
        print("Данные в таблицах")
        cur.execute("""
                        SELECT c.id, c.name, c.surname, c.email, n.number FROM client c
                        LEFT JOIN numbers n ON c.id = n.client_id
                        ORDER by c.id
                        """)
        pprint(cur.fetchall())
        print("Изменены данные клиента id: ",
              change_client(cur, 3, "Иван", "Егоров", '54623@outlook.com'))
        print("Телефон удалён c номером: ",
              delete_number(cur, '79895424635'))
        print("Данные в таблицах")
        cur.execute("""
                        SELECT c.id, c.name, c.surname, c.email, n.number FROM client c
                        LEFT JOIN numbers n ON c.id = n.client_id
                        ORDER by c.id
                        """)
        pprint(cur.fetchall())
        print("Клиент удалён с id: ",
              delete_client(cur, 2))
        cur.execute("""
                        SELECT c.id, c.name, c.surname, c.email, n.number FROM client c
                        LEFT JOIN numbers n ON c.id = n.client_id
                        ORDER by c.id
                        """)
        pprint(cur.fetchall())
        print('Найденный клиент по имени:')
        pprint(find_client(cur, 'Николай'))

        print('Найденный клиент по email:')
        pprint(find_client(cur, None, None, '54623@outlook.com'))

        print('Найденный клиент по имени, фамилии и email:')
        pprint(find_client(cur, 'Иван', 'Егоров',
                           '54623@outlook.com'))

        print('Найденный клиент по имени, фамилии, телефону и email:')
        pprint(find_client(cur, 'Николай', 'Постнов',
                           '3218K@gmail.com', '79625478235'))

        print('Найденный клиент по имени, фамилии, телефону:')
        pprint(find_client(cur, None, None, None, '79852146215'))
