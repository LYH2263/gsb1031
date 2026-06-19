-- Books
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('The Great Gatsby', 'F. Scott Fitzgerald', '9780743273565', 5, 5, 1, 'http://localhost:8000/uploads/great_gatsby.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('To Kill a Mockingbird', 'Harper Lee', '9780061120084', 3, 3, 1, 'http://localhost:8000/uploads/to_kill_a_mockingbird.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('1984', 'George Orwell', '9780451524935', 10, 10, 1, 'http://localhost:8000/uploads/1984.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('Python Crash Course', 'Eric Matthes', '9781593279288', 2, 2, 1, 'http://localhost:8000/uploads/python_crash_course.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('三体', '刘慈欣', '9787536692930', 5, 5, 1, 'http://localhost:8000/uploads/three_body_problem.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('活着', '余华', '9787506365437', 8, 8, 1, 'http://localhost:8000/uploads/to_live.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('红楼梦', '曹雪芹', '9787020002207', 10, 10, 1, 'http://localhost:8000/uploads/dream_of_red_chamber.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('西游记', '吴承恩', '9787020008735', 10, 10, 1, 'http://localhost:8000/uploads/journey_to_the_west.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('水浒传', '施耐庵', '9787020008728', 10, 10, 1, 'http://localhost:8000/uploads/water_margin.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('三国演义', '罗贯中', '9787020008711', 10, 10, 1, NULL);
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('围城', '钱钟书', '9787020024759', 6, 6, 1, 'http://localhost:8000/uploads/fortress_besieged.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('平凡的世界', '路遥', '9787530219218', 4, 4, 1, NULL);
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('骆驼祥子', '老舍', '9787020024758', 5, 5, 1, NULL);
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('边城', '沈从文', '9787540458027', 3, 3, 1, 'http://localhost:8000/uploads/border_town.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('许三观卖血记', '余华', '9787506365444', 4, 4, 1, NULL);
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('兄弟', '余华', '9787506365451', 2, 2, 1, NULL);
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('狂人日记', '鲁迅', '9787530213889', 5, 5, 1, NULL);
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('百年孤独', '加西亚·马尔克斯', '9787544253994', 7, 7, 1, 'http://localhost:8000/uploads/one_hundred_years_of_solitude.jpg');
INSERT INTO books (title, author, isbn, total_copies, available_copies, is_active, cover_url) VALUES ('解忧杂货店', '东野圭吾', '9787544270878', 6, 6, 1, 'http://localhost:8000/uploads/miracles_of_namiya_general_store.jpg');

-- Users (password is 'password' for all)
INSERT INTO users (email, phone, hashed_password, role, is_active) VALUES ('admin@example.com', '13800138000', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin', 1);
INSERT INTO users (email, phone, hashed_password, role, is_active) VALUES ('user@example.com', '13900139000', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'user', 1);
