export interface User {
  id: number;
  phone: string;
  is_active: boolean;
  role: string;
}

export interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string;
  cover_url?: string;
  total_copies: number;
  available_copies: number;
  is_active: boolean;
  is_borrowing?: boolean;
  has_borrowed?: boolean;
}

export interface Borrow {
  id: number;
  user_id: number;
  book_id: number;
  borrow_date: string;
  return_date?: string;
  is_returned: boolean;
  book: Book;
}
