// 前端诊断脚本
const http = require('http');
const https = require('https');

console.log('🔍 CRM前端诊断工具');
console.log('====================');

// 测试后端连接
function testBackend() {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 5000,
      path: '/api/v1/test',
      method: 'GET',
      timeout: 5000
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        console.log(`✅ 后端连接测试: HTTP ${res.statusCode}`);
        resolve(true);
      });
    });

    req.on('error', (err) => {
      console.log(`❌ 后端连接失败: ${err.message}`);
      resolve(false);
    });

    req.on('timeout', () => {
      console.log('❌ 后端连接超时');
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

// 测试前端连接
function testFrontend() {
  return new Promise((resolve) => {
    const options = {
      hostname: 'localhost',
      port: 3000,
      path: '/',
      method: 'GET',
      timeout: 5000
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      res.on('end', () => {
        console.log(`✅ 前端连接测试: HTTP ${res.statusCode}`);

        // 检查是否返回了正确的HTML
        if (data.includes('<!DOCTYPE html>') && data.includes('酒店家具CRM系统')) {
          console.log('✅ 前端HTML内容正常');
          resolve(true);
        } else {
          console.log('⚠️ 前端HTML内容异常');
          resolve(false);
        }
      });
    });

    req.on('error', (err) => {
      console.log(`❌ 前端连接失败: ${err.message}`);
      resolve(false);
    });

    req.on('timeout', () => {
      console.log('❌ 前端连接超时');
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

// 测试客户API
function testCustomerAPI() {
  return new Promise((resolve) => {
    // 先登录获取token
    const loginData = JSON.stringify({
      username: 'admin',
      password: 'admin123'
    });

    const loginOptions = {
      hostname: 'localhost',
      port: 5000,
      path: '/api/v1/auth/login',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(loginData)
      },
      timeout: 5000
    };

    const loginReq = http.request(loginOptions, (loginRes) => {
      let loginData = '';
      loginRes.on('data', (chunk) => {
        loginData += chunk;
      });
      loginRes.on('end', () => {
        try {
          const result = JSON.parse(loginData);
          if (loginRes.statusCode === 200 && result.access_token) {
            console.log('✅ 登录成功，获取到token');

            // 使用token测试客户API
            const customerOptions = {
              hostname: 'localhost',
              port: 5000,
              path: '/api/v1/customers',
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${result.access_token}`
              },
              timeout: 5000
            };

            const customerReq = http.request(customerOptions, (customerRes) => {
              let customerData = '';
              customerRes.on('data', (chunk) => {
                customerData += chunk;
              });
              customerRes.on('end', () => {
                if (customerRes.statusCode === 200) {
                  const customers = JSON.parse(customerData);
                  console.log(`✅ 客户API测试成功: 获取到 ${customers.customers?.length || 0} 个客户`);
                  resolve(true);
                } else {
                  console.log(`❌ 客户API返回错误: HTTP ${customerRes.statusCode}`);
                  resolve(false);
                }
              });
            });

            customerReq.on('error', (err) => {
              console.log(`❌ 客户API请求失败: ${err.message}`);
              resolve(false);
            });

            customerReq.on('timeout', () => {
              console.log('❌ 客户API请求超时');
              customerReq.destroy();
              resolve(false);
            });

            customerReq.end();
          } else {
            console.log(`❌ 登录失败: HTTP ${loginRes.statusCode}`);
            resolve(false);
          }
        } catch (err) {
          console.log(`❌ 登录响应解析失败: ${err.message}`);
          resolve(false);
        }
      });
    });

    loginReq.on('error', (err) => {
      console.log(`❌ 登录请求失败: ${err.message}`);
      resolve(false);
    });

    loginReq.on('timeout', () => {
      console.log('❌ 登录请求超时');
      loginReq.destroy();
      resolve(false);
    });

    loginReq.write(loginData);
    loginReq.end();
  });
}

// 检查端口状态
function checkPorts() {
  console.log('\n📊 端口状态检查:');

  // 检查3000端口
  const frontendCheck = new Promise((resolve) => {
    const req = http.request({
      hostname: 'localhost',
      port: 3000,
      path: '/',
      method: 'HEAD',
      timeout: 3000
    }, (res) => {
      console.log(`  ✅ 端口 3000 (前端): 监听中`);
      resolve(true);
    });

    req.on('error', () => {
      console.log(`  ❌ 端口 3000 (前端): 未监听`);
      resolve(false);
    });

    req.on('timeout', () => {
      console.log(`  ⚠️ 端口 3000 (前端): 连接超时`);
      req.destroy();
      resolve(false);
    });

    req.end();
  });

  // 检查5000端口
  const backendCheck = new Promise((resolve) => {
    const req = http.request({
      hostname: 'localhost',
      port: 5000,
      path: '/api/v1/test',
      method: 'HEAD',
      timeout: 3000
    }, (res) => {
      console.log(`  ✅ 端口 5000 (后端): 监听中`);
      resolve(true);
    });

    req.on('error', () => {
      console.log(`  ❌ 端口 5000 (后端): 未监听`);
      resolve(false);
    });

    req.on('timeout', () => {
      console.log(`  ⚠️ 端口 5000 (后端): 连接超时`);
      req.destroy();
      resolve(false);
    });

    req.end();
  });

  return Promise.all([frontendCheck, backendCheck]);
}

// 主诊断函数
async function diagnose() {
  console.log('\n🚀 开始诊断...\n');

  // 检查端口
  await checkPorts();

  console.log('\n🔧 服务连接测试:');
  const backendOk = await testBackend();
  const frontendOk = await testFrontend();

  console.log('\n🔐 API功能测试:');
  const apiOk = await testCustomerAPI();

  console.log('\n📋 诊断结果汇总:');
  console.log('====================');
  console.log(`后端服务: ${backendOk ? '✅ 正常' : '❌ 异常'}`);
  console.log(`前端服务: ${frontendOk ? '✅ 正常' : '❌ 异常'}`);
  console.log(`API功能: ${apiOk ? '✅ 正常' : '❌ 异常'}`);

  if (backendOk && frontendOk && apiOk) {
    console.log('\n🎉 所有测试通过！系统应该可以正常工作。');
    console.log('\n🔗 访问链接:');
    console.log('  前端: http://localhost:3000');
    console.log('  后端: http://localhost:5000');
    console.log('  客户管理: http://localhost:3000/customers');
    console.log('\n🔑 登录信息:');
    console.log('  用户名: admin');
    console.log('  密码: admin123');
  } else {
    console.log('\n⚠️ 发现问题，请检查以上错误信息。');

    if (!backendOk) {
      console.log('\n💡 后端问题建议:');
      console.log('  1. 检查后端服务是否启动: cd backend && python run_app.py');
      console.log('  2. 检查5000端口是否被占用');
    }

    if (!frontendOk) {
      console.log('\n💡 前端问题建议:');
      console.log('  1. 检查前端服务是否启动: cd frontend && npm start');
      console.log('  2. 清除浏览器缓存后重试');
      console.log('  3. 检查控制台是否有JavaScript错误');
    }

    if (!apiOk) {
      console.log('\n💡 API问题建议:');
      console.log('  1. 检查数据库连接');
      console.log('  2. 检查认证中间件配置');
    }
  }
}

// 运行诊断
diagnose().catch(err => {
  console.error('诊断过程中出现错误:', err);
});