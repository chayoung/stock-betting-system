import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { TrendingUp, BarChart3, Activity, Calendar, Play, ShieldCheck, ShoppingCart, Tag } from 'lucide-react';

const App = () => {
  const [data, setData] = useState(null);
  const [todayTrades, setTodayTrades] = useState([]);
  const [historyTrades, setHistoryTrades] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 분석 기간 상태 관리 (기본값: 오늘부터 7일 전 ~ 오늘)
  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 7);
    return d.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => {
    return new Date().toISOString().split('T')[0];
  });
  const [notify, setNotify] = useState(false);

  // 어드민 로그인 상태 관리
  const [isLoggedIn, setIsLoggedIn] = useState(() => {
    return localStorage.getItem('isLoggedIn') === 'true';
  });
  const [adminId, setAdminId] = useState(() => localStorage.getItem('adminId') || '');
  const [adminPassword, setAdminPassword] = useState(() => localStorage.getItem('adminPassword') || '');
  const [showLoginModal, setShowLoginModal] = useState(false);

  const handleLogin = async () => {
    try {
      const response = await axios.post('/api/login', {
        username: adminId,
        password: adminPassword
      });
      if (response.data.status === 'success') {
        setIsLoggedIn(true);
        localStorage.setItem('isLoggedIn', 'true');
        localStorage.setItem('adminId', adminId);
        localStorage.setItem('adminPassword', adminPassword);
        setShowLoginModal(false);
        alert('로그인 성공');
      }
    } catch (err) {
      alert('로그인 실패: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setAdminId('');
    setAdminPassword('');
    localStorage.removeItem('isLoggedIn');
    localStorage.removeItem('adminId');
    localStorage.removeItem('adminPassword');
    alert('로그아웃 되었습니다.');
  };

  const runKisTask = async (taskType, mode = 'buy') => {
    setLoading(true);
    try {
      const url = taskType === 'test'
        ? '/api/kis/test'
        : `/api/kis/batch?mode=${mode}&force=true`;

      const response = await axios.post(url, {}, {
        headers: { 'X-Admin-Password': adminPassword }
      });
      alert(response.data.message);
    } catch (err) {
      alert('작업 요청 실패: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const fetchBacktest = async (isInitial = false) => {
    setLoading(true);
    try {
      // 파라미터가 없을 때만 백엔드가 최근 5일을 자동 계산함
      const url = isInitial
        ? `/api/backtest?notify=${notify}`
        : `/api/backtest?start=${startDate}&end=${endDate}&notify=${notify}`;

      const response = await axios.get(url);
      setData(response.data);

      // 백엔드에서 결정된 실제 날짜로 UI 업데이트
      if (response.data.start_date && response.data.end_date) {
        setStartDate(response.data.start_date);
        setEndDate(response.data.end_date);
      }
      setError(null);
    } catch (err) {
      setError('백엔드 서버에 연결할 수 없습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchTodayTrades = async () => {
    try {
      const response = await axios.get('/api/today_trades');
      if (response.data.status === 'success') {
        setTodayTrades(response.data.data);
      }
    } catch (err) {
      console.error('오늘의 매매 내역을 불러오는데 실패했습니다.', err);
    }
  };

  const fetchHistoryTrades = async () => {
    if (!startDate || !endDate) {
      alert("시작일과 종료일을 선택해주세요.");
      return;
    }
    setLoading(true);
    try {
      const url = `/api/trades_history?start=${startDate}&end=${endDate}`;
      const response = await axios.get(url);
      if (response.data.status === 'success') {
        setHistoryTrades(response.data.data);
      }
      setError(null);
    } catch (err) {
      setError('역대 매매 내역을 불러오는데 실패했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 마운트 시 오늘의 매매 내역 불러오기
    fetchTodayTrades();
  }, []);

  return (
    <div className="app-container">
      <header>
        <div>
          <h1>주식 종가배팅 시스템</h1>
          <p style={{ color: 'var(--text-muted)' }}>KOSPI / KOSDAQ 시뮬레이션 리포트</p>
        </div>
        <div className="header-actions">
          <div className="date-inputs">
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>시작일</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={{ padding: '0.5rem', borderRadius: '0.4rem', border: '1px solid var(--glass)', background: 'var(--bg-card)', color: 'white' }}
              />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem' }}>
              <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>종료일</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={{ padding: '0.5rem', borderRadius: '0.4rem', border: '1px solid var(--glass)', background: 'var(--bg-card)', color: 'white' }}
              />
            </div>
          </div>

          <div className="admin-buttons" style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                id="notify"
                checked={notify}
                onChange={(e) => setNotify(e.target.checked)}
                style={{ width: '1.2rem', height: '1.2rem', cursor: 'pointer' }}
              />
              <label htmlFor="notify" style={{ fontSize: '0.85rem', color: 'var(--text-main)', cursor: 'pointer' }}>알림</label>
            </div>
            {!isLoggedIn ? (
              <button className="btn" onClick={() => setShowLoginModal(true)} style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>Login</button>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
                <span className="admin-status" style={{ fontSize: '0.85rem', color: '#10b981', fontWeight: 'bold' }}>🔓 Admin</span>
                <button className="btn" onClick={handleLogout} style={{ padding: '0.5rem 1rem', fontSize: '0.85rem', background: '#ef4444' }}>Logout</button>
              </div>
            )}
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              <button className="btn" onClick={fetchBacktest} disabled={loading} style={{ padding: '0.5rem 1rem', fontSize: '0.85rem' }}>
                {loading ? '...' : '분석'}
              </button>
              <button className="btn" onClick={fetchHistoryTrades} disabled={loading} style={{ background: '#475569', fontSize: '0.85rem', padding: '0.5rem 1rem' }}>
                조회
              </button>
            </div>
          </div>
        </div>
      </header>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', borderRadius: '0.5rem', marginBottom: '2rem' }}>
          {error}
        </div>
      )}

      {/* KIS 서비스 제어 섹션 - 로그인 시에만 노출 */}
      {isLoggedIn && (
        <div className="card control-card" style={{ marginBottom: '2rem', background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
          <div>
            <h3 style={{ margin: 0, color: '#818cf8', display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
              <Play size={20} /> KIS 서비스 수동 제어
            </h3>
            <p style={{ margin: '0.3rem 0 0 0', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              백그라운드에서 KIS 모의투자 작업을 즉시 실행합니다. (결과: 텔레그램)
            </p>
          </div>
          <div className="control-buttons">
            <button className="btn" onClick={() => runKisTask('test')} style={{ background: '#10b981', display: 'flex', alignItems: 'center', gap: '0.4rem', justifyContent: 'center' }}>
              <ShieldCheck size={18} /> 계좌 정보 테스트
            </button>
            <button className="btn" onClick={() => runKisTask('batch', 'buy')} style={{ background: '#6366f1', display: 'flex', alignItems: 'center', gap: '0.4rem', justifyContent: 'center' }}>
              <ShoppingCart size={18} /> 매수 배치 실행
            </button>
            <button className="btn" onClick={() => runKisTask('batch', 'sell')} style={{ background: '#f59e0b', display: 'flex', alignItems: 'center', gap: '0.4rem', justifyContent: 'center' }}>
              <Tag size={18} /> 매도 배치 실행
            </button>
          </div>
        </div>
      )}

      {todayTrades && todayTrades.length > 0 && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📋 오늘의 자동 매매 내역 (배치 실행 결과)
          </h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>시간</th>
                  <th>구분</th>
                  <th>모의/실투</th>
                  <th>종목명</th>
                  <th>매도/매수가</th>
                  <th>수량</th>
                  <th>수익금</th>
                  <th>사유</th>
                </tr>
              </thead>
              <tbody>
                {todayTrades.map((trade, idx) => (
                  <tr key={idx}>
                    <td>{trade.date}</td>
                    <td>
                      <span style={{
                        padding: '0.2rem 0.5rem', borderRadius: '0.3rem', fontSize: '0.75rem', fontWeight: 'bold',
                        background: trade.action === 'BUY' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                        color: trade.action === 'BUY' ? '#ef4444' : '#3b82f6'
                      }}>
                        {trade.action === 'BUY' ? '매수' : '매도'}
                      </span>
                    </td>
                    <td>
                      <span style={{
                        padding: '0.2rem 0.5rem', borderRadius: '0.3rem', fontSize: '0.75rem', fontWeight: 'bold',
                        background: trade.trade_type === 'REAL' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                        color: trade.trade_type === 'REAL' ? '#10b981' : '#f59e0b'
                      }}>
                        {trade.trade_type === 'REAL' ? '실전투자' : '모의투자'}
                      </span>
                    </td>
                    <td>{trade.name} ({trade.symbol})</td>
                    <td>{Number(trade.price).toLocaleString()}원</td>
                    <td>{trade.qty > 0 ? `${trade.qty}주` : '-'}</td>
                    <td>
                      {trade.action === 'SELL' ? (
                        <span style={{ color: trade.profit > 0 ? '#ef4444' : trade.profit < 0 ? '#3b82f6' : 'inherit', fontWeight: 'bold' }}>
                          {trade.profit > 0 ? '+' : ''}{Number(trade.profit).toLocaleString()}원
                        </span>
                      ) : '-'}
                    </td>
                    <td>{trade.reason || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {historyTrades && historyTrades.length >= 0 && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            📜 선택 기간 투자 내역 ({startDate} ~ {endDate})
          </h3>
          {historyTrades.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>해당 기간에 실행된 투자 내역이 없습니다.</p>
          ) : (
            <>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>시간</th>
                      <th>구분</th>
                      <th>모의/실투</th>
                      <th>종목명</th>
                      <th>매도/매수가</th>
                      <th>수량</th>
                      <th>수익금</th>
                      <th>사유</th>
                    </tr>
                  </thead>
                  <tbody>
                    {historyTrades.map((trade, idx) => (
                      <tr key={idx}>
                        <td>{trade.date}</td>
                        <td>
                          <span style={{
                            padding: '0.2rem 0.5rem', borderRadius: '0.3rem', fontSize: '0.75rem', fontWeight: 'bold',
                            background: trade.action === 'BUY' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                            color: trade.action === 'BUY' ? '#ef4444' : '#3b82f6'
                          }}>
                            {trade.action === 'BUY' ? '매수' : '매도'}
                          </span>
                        </td>
                        <td>
                          <span style={{
                            padding: '0.2rem 0.5rem', borderRadius: '0.3rem', fontSize: '0.75rem', fontWeight: 'bold',
                            background: trade.trade_type === 'REAL' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                            color: trade.trade_type === 'REAL' ? '#10b981' : '#f59e0b'
                          }}>
                            {trade.trade_type === 'REAL' ? '실전투자' : '모의투자'}
                          </span>
                        </td>
                        <td>{trade.name} ({trade.symbol})</td>
                        <td>{Number(trade.price).toLocaleString()}원</td>
                        <td>{trade.qty > 0 ? `${trade.qty}주` : '-'}</td>
                        <td>
                          {trade.action === 'SELL' ? (
                            <span style={{ color: trade.profit > 0 ? '#ef4444' : trade.profit < 0 ? '#3b82f6' : 'inherit', fontWeight: 'bold' }}>
                              {trade.profit > 0 ? '+' : ''}{Number(trade.profit).toLocaleString()}원
                            </span>
                          ) : '-'}
                        </td>
                        <td>{trade.reason || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* 누적 데이터 요약 */}
              {(() => {
                const sellTrades = historyTrades.filter(t => t.action === 'SELL');
                const totalProfit = sellTrades.reduce((acc, t) => acc + (t.profit || 0), 0);
                const totalPrincipal = sellTrades.reduce((acc, t) => acc + (t.price * t.qty - (t.profit || 0)), 0);
                const returnRate = totalPrincipal > 0 ? (totalProfit / totalPrincipal) * 100 : 0;

                return (
                  <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--bg-main)', borderRadius: '0.5rem', border: '1px solid var(--border)', display: 'flex', gap: '2rem', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>누적 수익금(선택 기간):</span>
                      <strong style={{ fontSize: '1.2rem', color: totalProfit > 0 ? '#ef4444' : totalProfit < 0 ? '#3b82f6' : 'inherit' }}>
                        {totalProfit > 0 ? '+' : ''}{totalProfit.toLocaleString()}원
                      </strong>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span style={{ color: 'var(--text-muted)' }}>기간 수익률(실현손익):</span>
                      <strong style={{ fontSize: '1.2rem', color: returnRate > 0 ? '#ef4444' : returnRate < 0 ? '#3b82f6' : 'inherit' }}>
                        {returnRate > 0 ? '+' : ''}{returnRate.toFixed(2)}%
                      </strong>
                    </div>
                  </div>
                );
              })()}
            </>
          )}
        </div>
      )}

      {data && (
        <>
          <div className="stats-grid">
            <div className="card">
              <div className="stat-label"><TrendingUp size={16} inline /> 총 수익률</div>
              <div className={`stat-value ${data.summary.total_profit_rate > 0 ? 'up' : 'down'}`}>
                {data.summary.total_profit_rate.toFixed(2)}%
              </div>
            </div>
            <div className="card">
              <div className="stat-label"><Activity size={16} inline /> 승률</div>
              <div className="stat-value">{data.summary.win_rate.toFixed(2)}%</div>
            </div>
            <div className="card">
              <div className="stat-label"><BarChart3 size={16} inline /> 총 거래 횟수</div>
              <div className="stat-value">{data.summary.total_trades}회</div>
            </div>
            <div className="card">
              <div className="stat-label"><Calendar size={16} inline /> 분석 기간</div>
              <div className="stat-value" style={{ fontSize: '1.2rem' }}>{data.summary.period}</div>
            </div>
          </div>

          <div className="chart-container">
            <h3>일별 수익률 추이</h3>
            <div style={{ width: '100%', height: 400 }}>
              <ResponsiveContainer>
                <AreaChart data={data.daily_returns}>
                  <defs>
                    <linearGradient id="colorReturn" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
                  <XAxis dataKey="date" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                    itemStyle={{ color: '#f8fafc' }}
                  />
                  <Area type="monotone" dataKey="avg_return" name="전략 수익률" stroke="#6366f1" fillOpacity={1} fill="url(#colorReturn)" />
                  <Line type="monotone" dataKey="kospi_return" name="KOSPI 등락률" stroke="#94a3b8" strokeDasharray="5 5" dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3>상세 거래 내역</h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>날짜</th>
                    <th>시장</th>
                    <th>종목명</th>
                    <th>매수가(종가)</th>
                    <th>매도가(시가)</th>
                    <th>수량</th>
                    <th>수익금</th>
                    <th>수익률</th>
                  </tr>
                </thead>
                <tbody>
                  {data.trades.map((trade, idx) => (
                    <tr key={idx}>
                      <td>{trade.buy_date}</td>
                      <td>
                        <span style={{
                          fontSize: '0.75rem',
                          padding: '0.2rem 0.5rem',
                          borderRadius: '0.3rem',
                          background: trade.market === 'KOSPI' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(168, 85, 247, 0.2)',
                          color: trade.market === 'KOSPI' ? '#818cf8' : '#c084fc'
                        }}>
                          {trade.market}
                        </span>
                      </td>
                      <td>{trade.name}</td>
                      <td>{trade.buy_price.toLocaleString()}원</td>
                      <td>{trade.sell_price.toLocaleString()}원</td>
                      <td>{trade.invested && trade.buy_price ? `${Math.floor(trade.invested / trade.buy_price)}주` : '-'}</td>
                      <td>
                        <span style={{ color: trade.profit_krw > 0 ? '#ef4444' : trade.profit_krw < 0 ? '#3b82f6' : 'inherit', fontWeight: 'bold' }}>
                          {trade.profit_krw > 0 ? '+' : ''}{Number(trade.profit_krw || 0).toLocaleString()}원
                        </span>
                      </td>
                      <td className={trade.profit_rate > 0 ? 'up' : 'down'}>
                        {trade.profit_rate.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
      {/* Login Modal */}
      {showLoginModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>Admin Login</h2>
            </div>
            <div className="modal-body">
              <div className="input-group">
                <label>Admin ID</label>
                <input
                  type="text"
                  placeholder="아이디를 입력하세요"
                  value={adminId}
                  onChange={(e) => setAdminId(e.target.value)}
                />
              </div>
              <div className="input-group">
                <label>Password</label>
                <input
                  type="password"
                  placeholder="비밀번호를 입력하세요"
                  value={adminPassword}
                  onChange={(e) => setAdminPassword(e.target.value)}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn" onClick={handleLogin} style={{ background: '#6366f1' }}>로그인</button>
              <button className="btn" onClick={() => setShowLoginModal(false)} style={{ background: '#475569' }}>취소</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
