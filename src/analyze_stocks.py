#!/usr/bin/env python3
"""
當沖股票分析程式
分析並篩選符合3%獲利潛力的當沖標的
"""

import sys
sys.path.append('/opt/.manus/.sandbox-runtime')
from data_api import ApiClient
import json
from datetime import datetime, timedelta

def analyze_stock(symbol, name, client):
    """
    分析單一股票的當沖潛力
    
    參數:
    - symbol: 股票代號 (台股需加上.TW或.TWO)
    - name: 股票名稱
    - client: API客戶端
    
    返回:
    - 分析結果字典
    """
    try:
        # 獲取股票資料 (最近5天)
        response = client.call_api('YahooFinance/get_stock_chart', query={
            'symbol': symbol,
            'region': 'TW',
            'interval': '1d',
            'range': '5d',
            'includeAdjustedClose': True
        })
        
        if not response or 'chart' not in response or 'result' not in response['chart']:
            return None
            
        result = response['chart']['result'][0]
        meta = result['meta']
        timestamps = result['timestamp']
        quotes = result['indicators']['quote'][0]
        
        # 計算技術指標
        current_price = meta.get('regularMarketPrice', 0)
        day_high = meta.get('regularMarketDayHigh', 0)
        day_low = meta.get('regularMarketDayLow', 0)
        volume = meta.get('regularMarketVolume', 0)
        prev_close = meta.get('previousClose', 0)
        
        # 計算當日漲跌幅
        if prev_close > 0:
            daily_change_pct = ((current_price - prev_close) / prev_close) * 100
        else:
            daily_change_pct = 0
        
        # 計算當日振幅
        if prev_close > 0:
            amplitude = ((day_high - day_low) / prev_close) * 100
        else:
            amplitude = 0
        
        # 計算平均成交量 (過去5天)
        volumes = [v for v in quotes['volume'] if v is not None]
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        
        # 計算平均波動度 (過去5天)
        amplitudes = []
        for i in range(1, len(timestamps)):
            if quotes['high'][i] and quotes['low'][i] and quotes['close'][i-1]:
                amp = ((quotes['high'][i] - quotes['low'][i]) / quotes['close'][i-1]) * 100
                amplitudes.append(amp)
        avg_amplitude = sum(amplitudes) / len(amplitudes) if amplitudes else 0
        
        # 計算近期趨勢 (5日漲跌幅)
        closes = [c for c in quotes['close'] if c is not None]
        if len(closes) >= 2:
            trend_5d = ((closes[-1] - closes[0]) / closes[0]) * 100
        else:
            trend_5d = 0
        
        # 評分系統
        score = 0
        reasons = []
        
        # 1. 成交量評分 (30分)
        if volume > 50000:
            score += 30
            reasons.append(f"成交量充足({volume:,}張)")
        elif volume > 20000:
            score += 20
            reasons.append(f"成交量良好({volume:,}張)")
        elif volume > 10000:
            score += 10
            reasons.append(f"成交量尚可({volume:,}張)")
        
        # 2. 波動度評分 (30分)
        if amplitude > 5:
            score += 30
            reasons.append(f"當日振幅大({amplitude:.2f}%)")
        elif amplitude > 3:
            score += 20
            reasons.append(f"當日振幅中等({amplitude:.2f}%)")
        elif amplitude > 2:
            score += 10
            reasons.append(f"當日振幅尚可({amplitude:.2f}%)")
        
        # 3. 趨勢評分 (20分)
        if 0 < daily_change_pct < 8:
            score += 20
            reasons.append(f"當日漲勢健康({daily_change_pct:.2f}%)")
        elif daily_change_pct > 0:
            score += 10
            reasons.append(f"當日上漲({daily_change_pct:.2f}%)")
        
        # 4. 平均波動度評分 (20分)
        if avg_amplitude > 4:
            score += 20
            reasons.append(f"平均波動度高({avg_amplitude:.2f}%)")
        elif avg_amplitude > 3:
            score += 15
            reasons.append(f"平均波動度良好({avg_amplitude:.2f}%)")
        elif avg_amplitude > 2:
            score += 10
            reasons.append(f"平均波動度尚可({avg_amplitude:.2f}%)")
        
        return {
            'symbol': symbol,
            'name': name,
            'current_price': current_price,
            'daily_change_pct': daily_change_pct,
            'amplitude': amplitude,
            'volume': volume,
            'avg_volume': avg_volume,
            'avg_amplitude': avg_amplitude,
            'trend_5d': trend_5d,
            'score': score,
            'reasons': reasons,
            'day_high': day_high,
            'day_low': day_low,
            'prev_close': prev_close
        }
        
    except Exception as e:
        print(f"分析 {name}({symbol}) 時發生錯誤: {str(e)}")
        return None

def main():
    """主程式"""
    client = ApiClient()
    
    # 待分析的股票清單 (基於成交量排行和題材熱度)
    stocks = [
        ('2409.TW', '友達'),
        ('3481.TW', '群創'),
        ('3037.TW', '欣興'),
        ('8150.TW', '南茂'),
        ('2312.TW', '金寶'),
        ('1802.TW', '台玻'),
        ('8110.TW', '華東'),
        ('1815.TWO', '富喬'),
        ('6282.TW', '康舒'),
        ('2485.TW', '兆赫'),
        ('1303.TW', '南亞'),
        ('2303.TW', '聯電'),
        ('1717.TW', '長興'),
        ('3231.TW', '緯創')
    ]
    
    print("=" * 80)
    print("當沖股票分析系統")
    print(f"分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    results = []
    
    for symbol, name in stocks:
        print(f"正在分析 {name}({symbol})...")
        analysis = analyze_stock(symbol, name, client)
        if analysis:
            results.append(analysis)
    
    # 按評分排序
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # 輸出結果
    print("\n" + "=" * 80)
    print("分析結果 (按評分排序)")
    print("=" * 80)
    print()
    
    for i, stock in enumerate(results[:10], 1):
        print(f"{i}. {stock['name']}({stock['symbol']})")
        print(f"   評分: {stock['score']}/100")
        print(f"   現價: ${stock['current_price']:.2f}")
        print(f"   當日漲跌: {stock['daily_change_pct']:+.2f}%")
        print(f"   當日振幅: {stock['amplitude']:.2f}%")
        print(f"   成交量: {stock['volume']:,}張")
        print(f"   平均波動度: {stock['avg_amplitude']:.2f}%")
        print(f"   5日趨勢: {stock['trend_5d']:+.2f}%")
        print(f"   優勢: {', '.join(stock['reasons'])}")
        print()
    
    # 儲存結果到JSON
    with open('/home/ubuntu/stock_analysis_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("分析結果已儲存至 /home/ubuntu/stock_analysis_results.json")
    
    return results

if __name__ == "__main__":
    main()
