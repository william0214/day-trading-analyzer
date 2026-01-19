#!/usr/bin/env python3
"""
建立當沖股票分析視覺化圖表
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import json

# 設定中文字體
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK TC', 'Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False

# 讀取分析結果
with open('/home/ubuntu/stock_analysis_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 選取前5名股票
top5_stocks = [
    {'name': '欣興', 'symbol': '3037', 'score': 95, 'amplitude': 6.54, 'volume': 45803, 'trend_5d': 14.76, 'today_change': 9.31},
    {'name': '友達', 'symbol': '2409', 'score': 94, 'amplitude': 4.57, 'volume': 282821, 'trend_5d': 8.91, 'today_change': 9.87},
    {'name': '金寶', 'symbol': '2312', 'score': 92, 'amplitude': 7.67, 'volume': 117468, 'trend_5d': 29.95, 'today_change': 8.75},
    {'name': '群創', 'symbol': '3481', 'score': 91, 'amplitude': 4.64, 'volume': 78634, 'trend_5d': 21.85, 'today_change': 9.02},
    {'name': '南茂', 'symbol': '8150', 'score': 90, 'amplitude': 6.56, 'volume': 75388, 'trend_5d': 21.36, 'today_change': 6.35}
]

# 建立圖表
fig = plt.figure(figsize=(16, 10))
fig.suptitle('當沖股票分析報告 - 2026/01/19', fontsize=20, fontweight='bold', y=0.98)

# 1. 綜合評分雷達圖
ax1 = plt.subplot(2, 3, 1, projection='polar')
categories = ['綜合評分', '波動度', '成交量', '5日趨勢', '當日漲幅']
N = len(categories)

# 正規化數據
for stock in top5_stocks:
    values = [
        stock['score'],
        min(stock['amplitude'] * 10, 100),
        min(stock['volume'] / 3000, 100),
        min(stock['trend_5d'] * 3, 100),
        min(stock['today_change'] * 10, 100)
    ]
    values += values[:1]  # 閉合圖形
    
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    ax1.plot(angles, values, 'o-', linewidth=2, label=f"{stock['name']}({stock['symbol']})")
    ax1.fill(angles, values, alpha=0.15)

ax1.set_xticks(angles[:-1])
ax1.set_xticklabels(categories, fontsize=9)
ax1.set_ylim(0, 100)
ax1.set_title('五檔股票綜合評估', fontsize=12, fontweight='bold', pad=20)
ax1.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=8)
ax1.grid(True)

# 2. 成交量比較
ax2 = plt.subplot(2, 3, 2)
names = [f"{s['name']}\n({s['symbol']})" for s in top5_stocks]
volumes = [s['volume'] / 1000 for s in top5_stocks]  # 轉換為千張
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

bars = ax2.bar(names, volumes, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('成交量 (千張)', fontsize=11, fontweight='bold')
ax2.set_title('成交量比較', fontsize=12, fontweight='bold')
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# 在柱狀圖上標註數值
for bar, vol in zip(bars, volumes):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
             f'{vol:.1f}K',
             ha='center', va='bottom', fontsize=9, fontweight='bold')

# 3. 平均波動度比較
ax3 = plt.subplot(2, 3, 3)
amplitudes = [s['amplitude'] for s in top5_stocks]
bars = ax3.barh(names, amplitudes, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax3.set_xlabel('平均波動度 (%)', fontsize=11, fontweight='bold')
ax3.set_title('平均波動度比較', fontsize=12, fontweight='bold')
ax3.grid(axis='x', alpha=0.3, linestyle='--')
ax3.axvline(x=3, color='red', linestyle='--', linewidth=2, alpha=0.5, label='3%目標線')
ax3.legend(fontsize=9)

# 在橫條圖上標註數值
for bar, amp in zip(bars, amplitudes):
    width = bar.get_width()
    ax3.text(width, bar.get_y() + bar.get_height()/2.,
             f'{amp:.2f}%',
             ha='left', va='center', fontsize=9, fontweight='bold', 
             bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# 4. 5日趨勢比較
ax4 = plt.subplot(2, 3, 4)
trends = [s['trend_5d'] for s in top5_stocks]
bars = ax4.bar(names, trends, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax4.set_ylabel('5日漲跌幅 (%)', fontsize=11, fontweight='bold')
ax4.set_title('5日趨勢比較', fontsize=12, fontweight='bold')
ax4.grid(axis='y', alpha=0.3, linestyle='--')
ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)

# 在柱狀圖上標註數值
for bar, trend in zip(bars, trends):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
             f'{trend:+.1f}%',
             ha='center', va='bottom', fontsize=9, fontweight='bold')

# 5. 當日漲幅比較
ax5 = plt.subplot(2, 3, 5)
today_changes = [s['today_change'] for s in top5_stocks]
bars = ax5.bar(names, today_changes, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax5.set_ylabel('當日漲幅 (%)', fontsize=11, fontweight='bold')
ax5.set_title('當日漲幅比較', fontsize=12, fontweight='bold')
ax5.grid(axis='y', alpha=0.3, linestyle='--')
ax5.axhline(y=3, color='green', linestyle='--', linewidth=2, alpha=0.5, label='3%目標')
ax5.axhline(y=10, color='red', linestyle='--', linewidth=2, alpha=0.5, label='10%漲停')
ax5.legend(fontsize=9)

# 在柱狀圖上標註數值
for bar, change in zip(bars, today_changes):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height,
             f'{change:+.2f}%',
             ha='center', va='bottom', fontsize=9, fontweight='bold')

# 6. 綜合評分排名
ax6 = plt.subplot(2, 3, 6)
scores = [s['score'] for s in top5_stocks]
bars = ax6.barh(names, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
ax6.set_xlabel('綜合評分', fontsize=11, fontweight='bold')
ax6.set_title('綜合評分排名', fontsize=12, fontweight='bold')
ax6.set_xlim(85, 100)
ax6.grid(axis='x', alpha=0.3, linestyle='--')

# 在橫條圖上標註數值和排名
for i, (bar, score) in enumerate(zip(bars, scores), 1):
    width = bar.get_width()
    ax6.text(width - 1, bar.get_y() + bar.get_height()/2.,
             f'#{i} {score}分',
             ha='right', va='center', fontsize=10, fontweight='bold', color='white',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='black', alpha=0.7))

plt.tight_layout()
plt.savefig('/home/ubuntu/day_trading_analysis.png', dpi=300, bbox_inches='tight', facecolor='white')
print("視覺化圖表已儲存至 /home/ubuntu/day_trading_analysis.png")

# 建立簡化版摘要圖表
fig2, ax = plt.subplots(figsize=(12, 8), facecolor='white')
ax.axis('off')

# 標題
title_text = '當沖股票推薦 - 2026/01/19'
ax.text(0.5, 0.95, title_text, ha='center', va='top', fontsize=24, fontweight='bold',
        bbox=dict(boxstyle='round,pad=1', facecolor='#4ECDC4', alpha=0.8))

# 建立表格
table_data = []
table_data.append(['排名', '股票', '代號', '評分', '當日漲幅', '波動度', '成交量', '5日趨勢'])

for i, stock in enumerate(top5_stocks, 1):
    table_data.append([
        f'#{i}',
        stock['name'],
        stock['symbol'],
        f"{stock['score']}分",
        f"{stock['today_change']:+.2f}%",
        f"{stock['amplitude']:.2f}%",
        f"{stock['volume']/1000:.1f}K",
        f"{stock['trend_5d']:+.1f}%"
    ])

table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                bbox=[0.05, 0.35, 0.9, 0.5])

table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1, 2.5)

# 設定表頭樣式
for i in range(8):
    cell = table[(0, i)]
    cell.set_facecolor('#FF6B6B')
    cell.set_text_props(weight='bold', color='white', fontsize=12)

# 設定資料列樣式
row_colors = ['#FFE5E5', '#E5F9F7', '#E5F2F9', '#FFF0E5', '#E5F9F0']
for i in range(1, 6):
    for j in range(8):
        cell = table[(i, j)]
        cell.set_facecolor(row_colors[i-1])
        if j == 0:  # 排名欄
            cell.set_text_props(weight='bold', fontsize=13)

# 添加說明文字
note_text = """
操作建議：
• 嚴格執行停損（1.5-2%）  • 分批進場，控制部位  • 關注關鍵價位
• 目標獲利：3%           • 最佳時段：09:00-11:00  • 風險提示：注意高檔震盪

免責聲明：本報告僅供參考，不構成投資建議。股票投資有風險，請謹慎操作。
"""

ax.text(0.5, 0.15, note_text, ha='center', va='top', fontsize=10,
        bbox=dict(boxstyle='round,pad=1', facecolor='#FFF9E5', alpha=0.8),
        multialignment='left')

plt.savefig('/home/ubuntu/day_trading_summary.png', dpi=300, bbox_inches='tight', facecolor='white')
print("摘要圖表已儲存至 /home/ubuntu/day_trading_summary.png")

print("\n圖表生成完成！")
