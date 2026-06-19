import React, { useEffect, useState } from 'react';
import { Table, Button, message, Tag } from 'antd';
import type { Borrow } from '../types';
import api from '../services/api';

const MyBooks: React.FC = () => {
  const [borrows, setBorrows] = useState<Borrow[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchBorrows = async () => {
    setLoading(true);
    try {
      const response = await api.get('/my-borrows');
      setBorrows(response.data);
    } catch (error) {
      message.error('获取借阅记录失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBorrows();
  }, []);

  const handleReturn = async (borrowId: number) => {
    try {
      await api.post(`/borrows/${borrowId}/return`);
      message.success('归还成功');
      fetchBorrows();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '归还失败');
    }
  };

  const columns = [
    {
      title: '书名',
      key: 'book.title',
      render: (_: any, record: Borrow) => <span className="font-medium text-gray-900">{record.book.title}</span>,
    },
    {
      title: '作者',
      key: 'book.author',
      render: (_: any, record: Borrow) => <span className="text-gray-500">{record.book.author}</span>,
    },
    {
      title: '借阅日期',
      dataIndex: 'borrow_date',
      key: 'borrow_date',
      render: (date: string) => <span className="text-gray-600">{new Date(date).toLocaleDateString()}</span>,
    },
    {
      title: '归还日期',
      dataIndex: 'return_date',
      key: 'return_date',
      render: (date: string) => <span className="text-gray-600">{date ? new Date(date).toLocaleDateString() : '-'}</span>,
    },
    {
      title: '状态',
      key: 'status',
      render: (_: any, record: Borrow) => (
        <Tag 
            className={`rounded-full px-3 border-none ${record.is_returned ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'}`}
        >
          {record.is_returned ? '已归还' : '借阅中'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Borrow) => (
        !record.is_returned && (
          <Button 
            type="primary" 
            onClick={() => handleReturn(record.id)}
            className="ios-btn !h-8 !px-4 bg-ios-blue hover:bg-ios-lightblue shadow-md shadow-ios-blue/20"
          >
            归还
          </Button>
        )
      ),
    },
  ];

  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-1">我的借阅</h1>
        <p className="text-gray-500">管理您的借阅历史与归还状态</p>
      </div>
      <div className="glass-panel p-6 overflow-x-auto">
        <Table 
            columns={columns} 
            dataSource={borrows} 
            rowKey="id" 
            loading={loading} 
            pagination={{ pageSize: 8 }}
            scroll={{ x: 800 }}
        />
      </div>
    </div>
  );
};

export default MyBooks;
