import socket
import os

import torch
import numpy as np

from data.game_data import GameData
from data.proto import Frame, NnOutput, Vector2
from nn.model import LSTMModel, Model


def main():
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    model = LSTMModel().to(device)
    model.load_state_dict(torch.load(os.path.dirname(__file__) + "/model.pt"))
    model.eval()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("localhost", 6969))

    while True:
        # try:
        server.listen(1)
        print("Waiting for connection...")
        conn, addr = server.accept()
        with conn:
            print("Connected by", addr)

            game_data = GameData()
            x_history = []
            while True:
                data = conn.recv(1024)
                if not data:
                    print("no data")
                    break

                frame = Frame().parse(data)
                game_data.update_frame(frame)

                x = game_data.get_x()

                # print(x)

                x_history.append(x)
                # max length of 10
                if len(x_history) > 10:
                    x_history.pop(0)

                # pad with zeros if not enough data
                while len(x_history) < 10:
                    x_history.insert(0, np.zeros_like(x_history[0]))

                # print(x_history)
                # print(np.array([x_history]).shape)

                x_history_tensor = torch.tensor(np.array([x_history]), dtype=torch.float32, device=device)
                y = model(x_history_tensor).detach().cpu().numpy()[0]
                y = [float(o) for o in y]

                new_y = [0, 0]
                if y[0] > 0.5:
                    new_y[0] += 1
                if y[1] > 0.5:
                    new_y[0] -= 1
                if y[2] > 0.5:
                    new_y[1] += 1
                if y[3] > 0.5:
                    new_y[1] -= 1

                output = NnOutput()
                output.desired_move_direction = Vector2(x=new_y[0], y=new_y[1])

                print(new_y)

                conn.sendall(bytes(output))
        # except Exception as e:
        #     print(e)


if __name__ == "__main__":
    main()
