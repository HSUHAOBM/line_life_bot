"""
Rich Menu 管理後台 API
提供 Rich Menu 的 CRUD 操作
"""
from flask import Flask, render_template, jsonify, request, send_file
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob
)
from dotenv import load_dotenv
import os
from richmenu.rich_menu_alias import MENU_IDS
import io

load_dotenv()

app = Flask(__name__)
configuration = Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))


@app.route('/')
def index():
    """管理後台首頁"""
    return render_template('richmenu_manager.html')


@app.route('/api/richmenus', methods=['GET'])
def get_richmenus():
    """取得所有 Rich Menu 列表"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            response = line_bot_api.get_rich_menu_list()

            menus = []
            for menu in response.richmenus:
                # 找出對應的地區名稱
                region = None
                for r, mid in MENU_IDS.items():
                    if mid == menu.rich_menu_id:
                        region = r
                        break

                menus.append({
                    'richMenuId': menu.rich_menu_id,
                    'name': menu.name,
                    'region': region,
                    'chatBarText': menu.chat_bar_text,
                    'selected': menu.selected,
                    'size': {
                        'width': menu.size.width,
                        'height': menu.size.height
                    }
                })

            return jsonify({
                'success': True,
                'data': menus
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/richmenu/<menu_id>', methods=['GET'])
def get_richmenu(menu_id):
    """取得指定 Rich Menu 詳細資訊"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            menu = line_bot_api.get_rich_menu(menu_id)

            return jsonify({
                'success': True,
                'data': {
                    'richMenuId': menu.rich_menu_id,
                    'name': menu.name,
                    'chatBarText': menu.chat_bar_text,
                    'selected': menu.selected,
                    'size': menu.size.__dict__,
                    'areas': [area.__dict__ for area in menu.areas]
                }
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404


@app.route('/api/richmenu/<menu_id>/image', methods=['GET'])
def get_richmenu_image(menu_id):
    """取得 Rich Menu 圖片"""
    try:
        # 先從本地檔案讀取
        from richmenu.rich_menu_alias import MENU_IDS

        # 找到對應的區域
        region = None
        for r, mid in MENU_IDS.items():
            if mid == menu_id:
                region = r
                break

        if region:
            image_path = os.path.join('richmenu', f'rich_menu_{region}.png')
            if os.path.exists(image_path):
                return send_file(
                    image_path,
                    mimetype='image/png',
                    as_attachment=False
                )

        # 如果本地沒有，嘗試從 LINE API 下載
        with ApiClient(configuration) as api_client:
            blob_api = MessagingApiBlob(api_client)
            image_data = blob_api.get_rich_menu_image(menu_id)

            return send_file(
                io.BytesIO(image_data),
                mimetype='image/png',
                as_attachment=False
            )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404


@app.route('/api/richmenu/<menu_id>', methods=['DELETE'])
def delete_richmenu(menu_id):
    """刪除指定 Rich Menu"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.delete_rich_menu(menu_id)

            return jsonify({
                'success': True,
                'message': f'Rich Menu {menu_id} 已刪除'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/richmenu/default', methods=['GET'])
def get_default_richmenu():
    """取得預設 Rich Menu"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)

            # LINE SDK v3 使用 get_default_rich_menu_id
            response = line_bot_api.get_default_rich_menu_id()

            return jsonify({
                'success': True,
                'data': {
                    'richMenuId': response.rich_menu_id
                }
            })
    except Exception as e:
        # 如果沒有設定預設選單，返回 None 而不是錯誤
        return jsonify({
            'success': True,
            'data': {
                'richMenuId': None
            }
        })


@app.route('/api/richmenu/default', methods=['POST'])
def set_default_richmenu():
    """設定預設 Rich Menu"""
    try:
        data = request.get_json()
        menu_id = data.get('richMenuId')

        if not menu_id:
            return jsonify({
                'success': False,
                'error': '缺少 richMenuId'
            }), 400

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.set_default_rich_menu(menu_id)

            return jsonify({
                'success': True,
                'message': f'已設定 {menu_id} 為預設 Rich Menu'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/richmenu/default', methods=['DELETE'])
def clear_default_richmenu():
    """清除預設 Rich Menu"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.delete_default_rich_menu()

            return jsonify({
                'success': True,
                'message': '已清除預設 Rich Menu'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/aliases', methods=['GET'])
def get_aliases():
    """取得所有 Rich Menu Alias"""
    try:
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            response = line_bot_api.get_rich_menu_alias_list()

            aliases = []
            for alias in response.aliases:
                aliases.append({
                    'aliasId': alias.rich_menu_alias_id,
                    'richMenuId': alias.rich_menu_id
                })

            return jsonify({
                'success': True,
                'data': aliases
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('ADMIN_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
