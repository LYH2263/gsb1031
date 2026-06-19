import React, { useState, useContext, useEffect } from 'react';
import { Form, Input, Button, Card, message, Typography, Modal } from 'antd';
import api from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const { Title } = Typography;

const Login: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const [sendingCode, setSendingCode] = useState(false);
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    let timer: any;
    if (countdown > 0) {
      timer = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [countdown]);

  const sendCode = async () => {
    try {
      const phone = form.getFieldValue('phone');
      if (!phone) {
        message.error('请输入手机号');
        return;
      }
      setSendingCode(true);
      const res = await api.post('/send-sms', { phone });
      
      Modal.info({
        title: '验证码已发送',
        content: `您的验证码是：${res.data.code}`,
        okText: '知道了',
      });
      
      setCountdown(60);
      setSendingCode(false);
    } catch (error: any) {
      setSendingCode(false);
      message.error(error.response?.data?.detail || '发送失败');
    }
  };

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      if (isLogin) {
        // Login
        const formData = new FormData();
        formData.append('username', values.phone);
        formData.append('password', values.password);
        
        const response = await api.post('/token', formData);
        login(response.data.access_token);
        message.success('登录成功');
        navigate('/');
      } else {
        // Register
        await api.post('/users/', {
          phone: values.phone,
          password: values.password,
          verification_code: values.verification_code
        });
        message.success('注册成功！请登录。');
        setIsLogin(true);
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '发生错误');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex justify-center items-center relative py-12">
      {/* Fixed Background Layer */}
      <div 
        className="fixed inset-0 bg-cover bg-center z-0" 
        style={{ backgroundImage: 'url("https://images.unsplash.com/photo-1557683316-973673baf926?q=80&w=2029&auto=format&fit=crop")' }}
      ></div>
      
      {/* Fixed Overlay Layer */}
      <div className="fixed inset-0 bg-white/30 backdrop-blur-sm z-0"></div>

      {/* Scrollable Content */}
      <Card className="glass-panel w-full max-w-[400px] mx-4 border-none !bg-white/60 relative z-10 animate-slide-up my-auto">
        <div className="text-center mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-ios-blue to-ios-cyan flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-ios-blue/30 mx-auto mb-3">
            L
          </div>
          <Title level={3} className="!text-gray-800 !mb-1 !text-2xl">{isLogin ? '欢迎回来' : '创建账号'}</Title>
          <p className="text-gray-500 text-sm">{isLogin ? '登录以管理您的图书' : '注册即可开启借阅之旅'}</p>
        </div>
        <Form
          form={form}
          name="basic"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="phone"
            rules={[{ required: true, message: '请输入手机号！' }]}
          >
            <Input className="ios-input" placeholder="手机号" prefix={<span className="text-gray-400 mr-2">📱</span>} />
          </Form.Item>

          {!isLogin && (
            <Form.Item required className="mb-4">
              <div className="flex gap-3">
                <Form.Item
                  name="verification_code"
                  noStyle
                  rules={[{ required: true, message: '请输入验证码！' }]}
                >
                  <Input className="ios-input" placeholder="验证码" prefix={<span className="text-gray-400 mr-2">🔢</span>} />
                </Form.Item>
                <Button onClick={sendCode} loading={sendingCode} disabled={countdown > 0} className="ios-btn !rounded-xl !h-auto">
                  {countdown > 0 ? `${countdown}s` : '获取验证码'}
                </Button>
              </div>
            </Form.Item>
          )}

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码！' }]}
          >
            <Input.Password className="ios-input" placeholder="密码" prefix={<span className="text-gray-400 mr-2">🔒</span>} />
          </Form.Item>

          <Form.Item className="mb-4">
            <Button type="primary" htmlType="submit" block loading={loading} className="ios-btn-primary h-11 text-lg">
              {isLogin ? '登录' : '注册'}
            </Button>
          </Form.Item>

          <div className="text-center">
            <Button type="link" onClick={() => setIsLogin(!isLogin)} className="text-gray-500 hover:text-ios-blue transition-colors">
              {isLogin ? '没有账号？立即注册' : '已有账号？立即登录'}
            </Button>
          </div>
          
          {/* Test Accounts Helper */}
          {isLogin && (
            <div className="mt-6 pt-6 border-t border-gray-100">
              <p className="text-xs text-gray-400 text-center mb-3">测试账号（点击自动填充）</p>
              <div className="flex justify-center gap-3">
                <Button 
                  size="small" 
                  className="text-xs bg-gray-50 text-gray-600 border-gray-200"
                  onClick={() => {
                    form.setFieldsValue({ phone: '13900000000', password: 'password' });
                  }}
                >
                  管理员: 13900000000
                </Button>
                <Button 
                  size="small" 
                  className="text-xs bg-gray-50 text-gray-600 border-gray-200"
                  onClick={() => {
                    form.setFieldsValue({ phone: '13800000000', password: 'password' });
                  }}
                >
                  用户: 13800000000
                </Button>
              </div>
            </div>
          )}
        </Form>
      </Card>
    </div>
  );
};

export default Login;
