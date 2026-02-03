import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area
} from 'recharts';
import { TrendingUp, BarChart3, Activity, Calendar } from 'lucide-react';

const App = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 분석 기간 상태 관리 (기본값은 빈 값으로 두어 백엔드 자동 계산 활용)
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [notify, setNotify] = useState(false);

  const fetchBacktest = async (isInitial = false) => {
    setLoading(true);
    try {
      // 파라미터가 없을 때만 백엔드가 최근 5일을 자동 계산함
      const url = isInitial
        ? `http://localhost:8000/api/backtest?notify=${notify}`
        : `http://localhost:8000/api/backtest?start=${startDate}&end=${endDate}&notify=${notify}`;

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

  useEffect(() => {
    // 마운트 시 최초 1회만 실행 (최근 5일 자동 조회)
    fetchBacktest(true);
  }, []);

  return (
    <div className="app-container">
      <header>
        <div>
          <h1>주식 종가배팅 시스템</h1>
          <p style={{ color: 'var(--text-muted)' }}>KOSPI / KOSDAQ 시뮬레이션 리포트</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', alignSelf: 'flex-end', paddingBottom: '0.5rem' }}>
            <input
              type="checkbox"
              id="notify"
              checked={notify}
              onChange={(e) => setNotify(e.target.checked)}
              style={{ width: '1.2rem', height: '1.2rem', cursor: 'pointer' }}
            />
            <label htmlFor="notify" style={{ fontSize: '0.875rem', color: 'var(--text-main)', cursor: 'pointer' }}>텔레그램 알림</label>
          </div>
          <button className="btn" onClick={fetchBacktest} disabled={loading} style={{ alignSelf: 'flex-end' }}>
            {loading ? '분석 중...' : '백테스트 실행'}
          </button>
        </div>
      </header>

      {error && (
        <div style={{ padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', borderRadius: '0.5rem', marginBottom: '2rem' }}>
          {error}
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
            <table>
              <thead>
                <tr>
                  <th>날짜</th>
                  <th>시장</th>
                  <th>종목명</th>
                  <th>매수가(종가)</th>
                  <th>매도가(시가)</th>
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
                    <td className={trade.profit_rate > 0 ? 'up' : 'down'}>
                      {trade.profit_rate.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default App;
