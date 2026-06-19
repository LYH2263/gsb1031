import React, { useEffect, useState, useContext } from 'react';
import { Button, message, Modal, Form, Input, InputNumber, Tag, Pagination, Empty, Upload } from 'antd';
import { SearchOutlined, EditOutlined, DeleteOutlined, PlusOutlined, ExclamationCircleOutlined, CheckCircleOutlined, ClockCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import type { Book } from '../types';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const DEFAULT_COVER = `${API_URL}/uploads/default_cover.jpg`;

const BookList: React.FC = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null); // Track editing book
  const [form] = Form.useForm();
  const [coverUrl, setCoverUrl] = useState<string>('');
  const [uploading, setUploading] = useState(false);
  const { user } = useContext(AuthContext);
  
  // New states for search and pagination
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 8;
  
  // Fetch books
  const fetchBooks = async () => {
    setLoading(true);
    try {
      const response = await api.get('/books/');
      setBooks(response.data);
    } catch (error) {
      message.error('获取图书列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBooks();
  }, []);

  const handleBorrow = async (bookId: number) => {
    try {
      await api.post('/borrows/', { book_id: bookId });
      message.success('借阅成功');
      fetchBooks(); // Refresh list to update availability
    } catch (error: any) {
      message.error(error.response?.data?.detail || '借阅失败');
    }
  };

  const handleDelete = (bookId: number) => {
    Modal.confirm({
        title: '确认删除',
        icon: <ExclamationCircleOutlined className="text-red-500" />,
        content: '您确定要删除这本书吗？此操作无法撤销。',
        okText: '删除',
        okType: 'danger',
        cancelText: '取消',
        centered: true,
        onOk: async () => {
            try {
                await api.delete(`/books/${bookId}`);
                message.success('删除成功');
                fetchBooks();
            } catch (error: any) {
                message.error('删除失败');
            }
        },
    });
  }

  const handleEdit = (book: Book) => {
    setEditingBook(book);
    setCoverUrl(book.cover_url || '');
    form.setFieldsValue({
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      total_copies: book.total_copies,
      available_copies: book.available_copies,
      cover_url: book.cover_url
    });
    setIsModalVisible(true);
  };

  const handleModalSubmit = async (values: any) => {
    try {
        if (editingBook) {
            // Edit mode
            await api.put(`/books/${editingBook.id}`, values);
            message.success('更新成功');
        } else {
            // Add mode
            await api.post('/books/', values);
            message.success('添加成功');
        }
        setIsModalVisible(false);
        setEditingBook(null); // Reset
        setCoverUrl('');
        form.resetFields();
        fetchBooks();
    } catch (error: any) {
        message.error(editingBook ? '更新失败' : '添加失败');
    }
  }

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingBook(null);
    setCoverUrl('');
    form.resetFields();
  }

  const handleUpload = async (options: any) => {
    const { onSuccess, onError, file } = options;
    const formData = new FormData();
    formData.append('file', file);
    setUploading(true);
    try {
        const response = await api.post('/upload/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        const url = response.data.url;
        setCoverUrl(url);
        form.setFieldsValue({ cover_url: url });
        onSuccess(url);
        message.success('封面上传成功');
    } catch (err) {
        onError({ err });
        message.error('封面上传失败');
    } finally {
        setUploading(false);
    }
  };

  // Filter and pagination logic
  const filteredBooks = books.filter(book => 
    book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.isbn.includes(searchTerm)
  );

  const currentBooks = filteredBooks.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  // Reset page when search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm]);

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
           <h1 className="text-3xl font-bold text-gray-900 mb-1">图书大厅</h1>
           <p className="text-gray-500">探索馆藏图书，发现知识海洋</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
          <Input 
            placeholder="搜索书名、作者..." 
            prefix={<SearchOutlined className="text-gray-400" />} 
            className="ios-input !rounded-full !bg-white/70 !border-none shadow-sm"
            style={{ minWidth: 260 }}
            allowClear
            onChange={e => setSearchTerm(e.target.value)}
          />
          
          {user?.role === 'admin' && (
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={() => {
                setEditingBook(null);
                form.resetFields();
                setIsModalVisible(true);
              }} 
              className="ios-btn-primary h-10 px-6 rounded-full"
            >
              添加图书
            </Button>
          )}
        </div>
      </div>
      
      {/* Grid Content */}
      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map(i => (
             <div key={i} className="glass-card h-80 animate-pulse bg-white/20"></div>
          ))}
        </div>
      ) : currentBooks.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {currentBooks.map(book => (
            <div key={book.id} className="glass-card p-0 flex flex-col h-full overflow-hidden group relative">
               {/* Cover Image */}
               <div className="h-48 relative overflow-hidden bg-gray-50">
                  <img 
                    src={book.cover_url || DEFAULT_COVER} 
                    alt={book.title}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  
                  {/* Hover Overlay with Action - Desktop */}
                  <div className="absolute inset-0 bg-black/5 backdrop-blur-[1px] transition-opacity duration-300 hidden lg:flex items-center justify-center opacity-0 lg:group-hover:opacity-100">
                     {book.is_borrowing ? (
                        <div className="flex flex-col items-center gap-2">
                            <div className="bg-ios-blue text-white px-4 py-2 rounded-full shadow-lg flex items-center gap-2">
                                <ClockCircleOutlined />
                                <span className="font-medium">正在借阅中</span>
                            </div>
                        </div>
                     ) : (
                        <Button 
                            type="primary" 
                            shape="round" 
                            size="large"
                            onClick={() => handleBorrow(book.id)} 
                            disabled={book.available_copies < 1}
                            className={book.available_copies > 0 ? "ios-btn-primary scale-90 group-hover:scale-100 transition-transform duration-300 shadow-xl" : "opacity-80"}
                        >
                            {book.available_copies > 0 ? '立即借阅' : '暂时缺货'}
                        </Button>
                     )}
                  </div>
               </div>
               
               {/* Content */}
               <div className="p-5 flex-1 flex flex-col bg-white/40">
                  <div className="mb-2">
                    <div className="flex justify-between items-start gap-2">
                        <h3 className="text-lg font-bold text-gray-900 leading-tight mb-1 line-clamp-1 flex-1" title={book.title}>{book.title}</h3>
                        {book.has_borrowed && !book.is_borrowing && (
                            <Tag icon={<CheckCircleOutlined />} color="success" className="rounded-full mr-0 border-none bg-green-100 text-green-600 shrink-0">
                                读过
                            </Tag>
                        )}
                    </div>
                    <p className="text-gray-500 text-sm line-clamp-1">{book.author}</p>
                  </div>
                  
                  <div className="mt-auto flex justify-between items-center pt-3 border-t border-white/30">
                     <div className="flex items-center gap-2">
                        <Tag 
                           color={book.available_copies > 0 ? "success" : "default"} 
                           className={`rounded-full px-2 border-none m-0 ${book.available_copies < 1 ? 'bg-gray-100 text-gray-500' : 'bg-green-100 text-green-600'}`}
                        >
                           {book.available_copies > 0 ? `${book.available_copies} 本` : '缺货'}
                        </Tag>
                        {/* Mobile Borrow Button */}
                        {book.is_borrowing ? (
                            <Tag color="processing" className="lg:hidden rounded-full border-none bg-blue-100 text-blue-600 m-0">
                                借阅中
                            </Tag>
                        ) : (
                            <Button 
                                type="primary" 
                                size="small" 
                                shape="round"
                                onClick={() => handleBorrow(book.id)}
                                disabled={book.available_copies < 1}
                                className={`lg:hidden text-xs h-6 ${book.available_copies > 0 ? "ios-btn-primary shadow-sm" : "opacity-50"}`}
                            >
                                借阅
                            </Button>
                        )}
                     </div>
                     
                     {user?.role === 'admin' && (
                        <div className="flex gap-1 opacity-100 lg:opacity-0 lg:group-hover:opacity-100 transition-opacity duration-200">
                           <Button type="text" size="small" icon={<EditOutlined />} onClick={() => handleEdit(book)} className="text-gray-500 hover:text-ios-blue rounded-full" />
                           <Button type="text" size="small" danger icon={<DeleteOutlined />} onClick={() => handleDelete(book.id)} className="rounded-full" />
                        </div>
                     )}
                  </div>
               </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="glass-panel p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
           <Empty description={<span className="text-gray-500">暂无相关图书</span>} />
        </div>
      )}

      {/* Pagination */}
      {filteredBooks.length > 0 && (
         <div className="flex justify-center mt-8 pb-8">
            <Pagination 
               current={currentPage} 
               total={filteredBooks.length} 
               pageSize={pageSize}
               onChange={setCurrentPage}
               showSizeChanger={false}
               hideOnSinglePage
            />
         </div>
      )}

      <Modal
        title={editingBook ? "编辑图书" : "添加新书"}
        open={isModalVisible}
        onCancel={handleCancel}
        footer={null}
        width={500}
        centered
      >
        <Form form={form} layout="vertical" onFinish={handleModalSubmit} size="large" className="pt-4">
            <Form.Item name="title" label="书名" rules={[{ required: true, message: '请输入书名' }]}>
                <Input className="ios-input" placeholder="请输入书名" />
            </Form.Item>
            <Form.Item name="author" label="作者" rules={[{ required: true, message: '请输入作者' }]}>
                <Input className="ios-input" placeholder="请输入作者" />
            </Form.Item>
            <Form.Item label="封面图片">
                <Upload
                    customRequest={handleUpload}
                    listType="picture-card"
                    showUploadList={false}
                    maxCount={1}
                    accept="image/*"
                >
                    {coverUrl ? (
                        <img src={coverUrl} alt="cover" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                        <div>
                            {uploading ? <LoadingOutlined /> : <PlusOutlined />}
                            <div style={{ marginTop: 8 }}>上传封面</div>
                        </div>
                    )}
                </Upload>
            </Form.Item>
            <Form.Item name="cover_url" hidden>
                <Input />
            </Form.Item>
            <div className="grid grid-cols-2 gap-4">
                <Form.Item name="isbn" label="ISBN" rules={[{ required: true, message: '请输入ISBN' }]}>
                    <Input className="ios-input" placeholder="请输入ISBN" />
                </Form.Item>
                <Form.Item name="total_copies" label="总数量" rules={[{ required: true, message: '请输入总数量' }]}>
                    <InputNumber min={1} style={{ width: '100%' }} className="ios-input" placeholder="数量" />
                </Form.Item>
            </div>
            {editingBook && (
                <Form.Item name="available_copies" label="可用数量" rules={[{ required: true, message: '请输入可用数量' }]}>
                    <InputNumber min={0} style={{ width: '100%' }} className="ios-input" placeholder="可用数量" />
                </Form.Item>
            )}
            <Form.Item className="mb-0 mt-4">
                <Button type="primary" htmlType="submit" block className="ios-btn-primary h-11">
                    {editingBook ? "保存更改" : "立即添加"}
                </Button>
            </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default BookList;