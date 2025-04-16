import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import colorsys

# 读取数据
df = pd.read_csv('新建 XLSX 工作表.csv')

def generate_colors(n, saturation=0.7, value=0.9):
    """生成和谐的颜色方案"""
    colors = []
    for i in range(n):
        hue = i / n
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append(f'rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, 0.6)')
    return colors

def create_sankey_diagram(df):
    # 准备数据
    dimensions = ['教学能力', '专业素养', '育人能力', '职业发展', '社会贡献']
    students = df['名称'].tolist()
    
    # 生成颜色方案
    student_colors = generate_colors(len(students), saturation=0.6, value=0.9)
    dimension_colors = generate_colors(len(dimensions), saturation=0.8, value=0.7)
    
    # 创建源和目标的映射
    sources = []
    targets = []
    values = []
    
    # 创建节点标签列表
    labels = students + dimensions
    
    # 为每个学生创建到维度的连接
    link_colors = []
    for student_idx, student in enumerate(students):
        student_data = df.loc[df['名称'] == student, ['桑葚图-'+dim for dim in dimensions]].values[0]
        student_color = student_colors[student_idx]
        for dim_idx, value in enumerate(student_data):
            if value > 0:
                sources.append(student_idx)
                targets.append(len(students) + dim_idx)
                values.append(value)
                # 使用学生对应的颜色，但降低不透明度
                base_color = student_color.replace('0.6', '0.3')
                link_colors.append(base_color)
    
    # 节点颜色列表
    node_colors = student_colors + dimension_colors

    # 创建桑基图
    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 20,
            thickness = 25,
            line = dict(color = "black", width = 0.5),
            label = labels,
            color = node_colors,
            customdata = labels,
            # 添加悬停文本
            hovertemplate = '节点: %{customdata}<br>总分值: %{value}<extra></extra>'
        ),
        link = dict(
            source = sources,
            target = targets,
            value = values,
            color = link_colors,
            hovertemplate = '从 %{source.customdata}<br>' +
                          '到 %{target.customdata}<br>' +
                          '分值: %{value:.1f}<extra></extra>'
        )
    )])

    # 更新布局
    fig.update_layout(
        title = dict(
            text = "教师评价维度分布图",
            font = dict(size=24, color='#333333'),
            x = 0.5,
            y = 0.95
        ),
        font = dict(
            family = "Arial, sans-serif",
            size = 12,
            color = "#333333"
        ),
        paper_bgcolor = 'rgba(250,250,250,0.9)',
        plot_bgcolor = 'rgba(250,250,250,0.9)',
        height = 800,
        width = 1200,
        showlegend = False,
        margin = dict(t=80, l=80, r=80, b=80),
        # 添加水印
        annotations=[
            dict(
                text="教师评价分析系统",
                x=0.97,
                y=0.03,
                showarrow=False,
                font=dict(
                    family="Arial",
                    size=10,
                    color="rgba(150,150,150,0.5)"
                ),
                xref="paper",
                yref="paper"
            )
        ]
    )

    # 添加交互配置
    fig.update_layout(
        hovermode = 'x',
        hoverlabel = dict(
            bgcolor = "white",
            font_size = 12,
            font_family = "Arial"
        )
    )

    return fig

def plot_radar(data, labels, title):
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    
    # 闭合图形
    data = np.concatenate((data, [data[0]]))
    angles = np.concatenate((angles, [angles[0]]))
    
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)
    
    ax.plot(angles, data, 'o-', linewidth=2)
    ax.fill(angles, data, alpha=0.25)
    
    ax.set_thetagrids(angles[:-1] * 180/np.pi, labels)
    ax.set_title(title, fontsize=15, pad=20)
    ax.grid(True)
    
    # 设置雷达图的范围
    ax.set_ylim(0, 5)
    
    return fig

# 绘制每个人的雷达图
radar_labels = ['教学效果', '创新能力', '沟通能力', '科研水平', '职业成长']
for index, row in df.iterrows():
    radar_data = row[6:11].values.astype(float)
    fig = plot_radar(radar_data, radar_labels, f"{row['名称']}的雷达图")
    plt.savefig(f'radar_{row["名称"]}.png')
    plt.close()

# 创建并保存桑基图
sankey_fig = create_sankey_diagram(df)
# 保存为HTML文件，启用更多交互功能
config = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'teacher_evaluation_sankey',
        'height': 800,
        'width': 1200,
        'scale': 2
    }
}
pio.write_html(sankey_fig, 'sankey_diagram.html', config=config)
print("图表绘制完成！")