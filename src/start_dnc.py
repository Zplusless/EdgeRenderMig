from DN.ffmpeg_controller.srv_ctl import dn_app

if __name__ == '__main__':
    dn_app.run('0.0.0.0', port=8000)