from flask import Flask, render_template
from Aggregated_Open_Interest_OHLC_History import chart_blueprint as chart_bp
from Open_Interest_History import chart_blueprint as other_bp

app = Flask(__name__)

app.register_blueprint(chart_bp, url_prefix='/Aggregated_Open_Interest_OHLC_History')
app.register_blueprint(other_bp, url_prefix='/Open_Interest_History')


# 导航栏视图函数
@app.route('/')
def index():
    return render_template('navbar.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8008)



