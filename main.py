import cv2
import mediapipe as mp
import pyautogui
from mediapipe.python.solutions.drawing_utils import _normalized_to_pixel_coordinates
from time import sleep
from time import time


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh

pyautogui.FAILSAFE = False

drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)


# configurações de tela e captura de vídeo
cap = cv2.VideoCapture(0)
width, height = pyautogui.size()
metade_largura = int(width/2)
metade_altura = int(height/2)


# variáveis de controle
boca = False
esquerdo = False
direito = False
olhos_fechados_start_time = None
cursor_ativo = True


with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as face_mesh:

  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image)

    # Draw the face mesh annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if (results.multi_face_landmarks):
        face_landmarks = results.multi_face_landmarks[0].landmark

    # coordenadas do olho direito
    olho_direito_cima = _normalized_to_pixel_coordinates(
        face_landmarks[159].x,
        face_landmarks[159].y,
        width,
        height)

    olho_direito_baixo = _normalized_to_pixel_coordinates(
        face_landmarks[145].x,
        face_landmarks[145].y,
        width,
        height)

    # coordenadas do olho esquerdo
    olho_esquerdo_cima = _normalized_to_pixel_coordinates(
        face_landmarks[386].x,
        face_landmarks[386].y,
        width,
        height)

    olho_esquerdo_baixo = _normalized_to_pixel_coordinates(
        face_landmarks[374].x,
        face_landmarks[374].y,
        width,
        height)

    nariz1 = _normalized_to_pixel_coordinates(
        face_landmarks[1].x,
        face_landmarks[1].y,
        width,
        height)

    try:
        nariz = width - nariz1[0]
    except:
        continue

    boca_cima = _normalized_to_pixel_coordinates(
        face_landmarks[13].x,
        face_landmarks[13].y,
        width,
        height)

    boca_baixo = _normalized_to_pixel_coordinates(
        face_landmarks[14].x,
        face_landmarks[14].y,
        width,
        height)

    # Vendo se a boca está aberta ou fechada
    if boca_baixo[1] - boca_cima[1] <= 5:
        boca = False
    if boca_baixo[1] - boca_cima[1] > 5:
        boca = True

    # Vendo se o olho direito está fechado
    if olho_direito_baixo[1] - olho_direito_cima[1] <= 10:
            direito = True
    if olho_direito_baixo[1] - olho_direito_cima[1] > 10 and direito:
            direito = False

    # Vendo se o olho esquerdo está fechado
    if olho_esquerdo_baixo[1] - olho_esquerdo_cima[1] <= 10:
            esquerdo = True
    if olho_esquerdo_baixo[1] - olho_esquerdo_cima[1] > 10 and esquerdo:
            esquerdo = False

    # Se o olho esquerdo estiver fechado, o olho direito aberto e a boca aberta, haverá um clique
    if boca and esquerdo and not direito and cursor_ativo:
        pyautogui.click()
        sleep(0.5)

    # Se o olho direito estiver fechado, a boca aberta e o olho esquerdo aberto, há um clique com o botão direito
    if direito and not esquerdo and boca and cursor_ativo:
        pyautogui.rightClick()
        sleep(0.5)

    # Se os olhos estão fechados, rastreie o tempo
    if direito and esquerdo:
        if olhos_fechados_start_time is None:
            olhos_fechados_start_time = time()  # Inicia a contagem de tempo quando os olhos são fechados
        else:
            tempo_olhos_fechados = time() - olhos_fechados_start_time

            # Se os olhos estão fechados por mais de 2 segundos, pare de mover o cursor
            if tempo_olhos_fechados >= 2:
                cursor_ativo = False
            else:
                cursor_ativo = True
    if not direito or not esquerdo:
        olhos_fechados_start_time = None  # Zera o tempo quando os olhos estão abertos ou apenas um olho está fechado

    # Se a boca estiver aberta e o cursor estiver ativo, mova o cursor
    if boca is False and cursor_ativo:
        # Quadros da tela (Divide a tela em quatro quadros para amplificar o movimento do cursor em função do movimento do nariz)
        # superior esquerdo
        if nariz < metade_largura and nariz1[1] < metade_altura:
            horizontal = metade_largura - nariz
            vertical = metade_altura - nariz1[1]
            pyautogui.moveTo(nariz - horizontal*4, nariz1[1] - vertical*6)

        # superior direito
        if nariz > metade_largura and nariz1[1] < metade_altura:
            vertical = metade_altura - nariz1[1]
            horizontal = nariz - metade_largura
            pyautogui.moveTo(nariz + horizontal*4, nariz1[1] - vertical*6)

        # inferior esquerdo
        if nariz < metade_largura and nariz1[1] > metade_altura:
            horizontal = metade_largura - nariz
            vertical = nariz1[1] - metade_altura
            pyautogui.moveTo(nariz - horizontal*4, nariz1[1] + vertical*6)

        # inferior direito
        if nariz > metade_largura and nariz1[1] > metade_altura:
            vertical = nariz1[1] - metade_altura
            horizontal = nariz - metade_largura
            pyautogui.moveTo(nariz + horizontal*4, nariz1[1] + vertical*6)

    # Flip the image horizontally for a selfie-view display.
    cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break

cap.release()
