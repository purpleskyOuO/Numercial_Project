import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import tkinter as tk
from PIL import Image, ImageTk

# 設定參數
Nx, Ny = 50, 50  # 網格尺寸
dt = 0.1  # 時間步長
dx = 1.0  # 空間步長

# 初始化汙染物濃度矩陣
concentration = np.zeros((Nx, Ny))


# 用於顯示gif動圖
class AnimatedGIF:
    def __init__(self, label, path):
        self.label = label
        self.path = path
        self.sequence = []
        self.delay = 100
        self.load_gif()

    def load_gif(self):
        image = Image.open(self.path)
        for frame in range(0, image.n_frames):
            image.seek(frame)
            frame_image = ImageTk.PhotoImage(image.copy())
            self.sequence.append(frame_image)
        self.delay = image.info.get('duration', 100)  # GIF幀持續時間

    def animate(self, counter):
        self.label.config(image=self.sequence[counter])
        counter += 1
        if counter == len(self.sequence):
            counter = 0
        self.label.after(self.delay, self.animate, counter)


def simulation():
    # 創建子視窗
    child_wd = tk.Toplevel(window)
    child_wd.title('模擬情形')
    child_wd.geometry("1200x600")
    child_wd.resizable(True, True)

    lbl_loading = tk.Label(child_wd, text='模擬中，請耐心等候...', font=font)
    lbl_loading.pack(anchor='center')

    # 關閉按鈕
    btn_close = tk.Button(child_wd, text='關閉', command=child_wd.destroy, font=font)
    btn_close.pack(side='bottom')

    # 製作動畫圖表
    # 檢查各係數輸入是否正常
    try:
        c = float(ent_concentration.get())
    except ValueError:
        c = 1000.0

    try:
        d = float(ent_D.get())
    except ValueError:
        d = 1.0

    try:
        t = float(ent_T.get())
    except ValueError:
        t = 50

    create_plot(c, d, t, isFixed.get())

    # 顯示gif動圖
    lbl_loading.destroy()
    lbl_gif = tk.Label(child_wd)
    lbl_gif.pack(anchor='center')

    gif_player = AnimatedGIF(lbl_gif, "pollutant_diffusion.gif")
    gif_player.animate(0)


# C = 汙染物濃度, D = 擴散係數, T = 模擬時間, fixed = 是否固定汙染源濃度
def create_plot(C, D, T, fixed):
    # 中心點的初始濃度
    global concentration
    center_x, center_y = Nx // 2, Ny // 2
    concentration[center_x, center_y] = C  # 中心點的汙染物濃度

    # 準備繪圖
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    img1 = ax1.imshow(concentration, origin='lower', cmap='viridis', vmin=0, vmax=1)
    img2 = ax2.imshow(concentration, origin='lower', cmap='viridis', vmin=0, vmax=C)
    fig.colorbar(img1, ax=ax1, orientation='horizontal')
    fig.colorbar(img2, ax=ax2, orientation='horizontal')
    ax1.set_title("pollutants Spread")
    ax2.set_title("pollutants Concentration")

    # 圖像更新
    def update(frame):
        global concentration
        new_virus_concentration = concentration.copy()

        # 更新汙染物濃度 (擴散方程)
        for i in range(1, Nx - 1):
            for j in range(1, Ny - 1):
                new_virus_concentration[i, j] = concentration[i, j] + D * dt * (
                        (concentration[i + 1, j] - 2 * concentration[i, j] + concentration[i - 1, j]) / dx ** 2 +
                        (concentration[i, j + 1] - 2 * concentration[i, j] + concentration[i, j - 1]) / dx ** 2
                )

        # 汙染源是否固定
        if fixed == 1:
            new_virus_concentration[center_x, center_y] = C

        # 邊界條件為0
        new_virus_concentration[0, :] = 0
        new_virus_concentration[-1, :] = 0
        new_virus_concentration[:, 0] = 0
        new_virus_concentration[:, -1] = 0

        # 更新矩陣
        concentration = new_virus_concentration.copy()

        # 更新圖像
        img1.set_data(concentration)
        img2.set_data(concentration)
        ax1.set_title(f"pollutants Spread (Time step: {frame})")
        ax2.set_title(f"pollutants Concentration (Time step: {frame})")
        return img1, img2

    # 創建動畫
    ani = FuncAnimation(fig, update, frames=np.arange(0, int(T / dt)), interval=50, blit=True)
    ani.save('pollutant_diffusion.gif')


# GUI基本設置
window = tk.Tk()
window.title('汙染物濃度擴散情形')
window.geometry('500x150')
window.resizable(False, False)

font = ("標楷體", 16)

# GUI元素
# 輸入汙染物濃度
lbl_concentration = tk.Label(window, text='釋放點汙染物濃度: ', font=font)
lbl_concentration.grid(row=2, column=1)
ent_concentration = tk.Entry(window, font=font)  # 未輸入預設為1000.0
ent_concentration.grid(row=2, column=2)

# 輸入擴散係數
lbl_D = tk.Label(window, text='汙染物擴散係數(m^2/s): ', font=font)
lbl_D.grid(row=3, column=1)
ent_D = tk.Entry(window, font=font)  # 未輸入預設值為1.0
ent_D.grid(row=3, column=2)

lbl_T = tk.Label(window, text='觀察時間(秒): ', font=font)
lbl_T.grid(row=4, column=1)
ent_T = tk.Entry(window, font=font)  # 未輸入預設值為50
ent_T.grid(row=4, column=2)

# 是否固定汙染源濃度
isFixed = tk.IntVar()
chk_source = tk.Checkbutton(window, text='固定汙染源濃度', font=font
                            , variable=isFixed, onvalue=1, offvalue=0)
chk_source.grid(row=5, column=1, columnspan=2)

# 模擬按鈕
btn_sim = tk.Button(window, text='模擬', command=simulation, font=font)
btn_sim.grid(row=7, column=1, columnspan=2)

window.mainloop()
