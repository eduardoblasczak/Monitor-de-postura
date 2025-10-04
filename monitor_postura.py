import cv2
import mediapipe as mp
import math

# Inicializando os módulos do MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# Função para calcular o ângulo entre três pontos
def calculate_angle(a, b, c):
    """Calcula o ângulo (em graus) formado por três pontos a, b, c."""
    # Coordenadas
    ax, ay = a.x, a.y
    bx, by = b.x, b.y
    cx, cy = c.x, c.y
    
    # Cálculo do ângulo usando a lei dos cossenos
    # Como as coordenadas são normalizadas, podemos usá-las diretamente
    angle = math.degrees(math.atan2(cy - by, cx - bx) - math.atan2(ay - by, ax - bx))
    
    # Garante que o ângulo seja positivo
    if angle < 0:
        angle += 360
        
    return angle

# Inicializa a captura de vídeo da webcam (0 é geralmente a webcam padrão)
cap = cv2.VideoCapture(0)

# Variável para armazenar o status da postura
posture_status = "Analisando..."

while cap.isOpened():
    # Lê um frame da webcam
    success, image = cap.read()
    if not success:
        print("Não foi possível acessar a webcam.")
        break

    # Para melhorar o desempenho, marcamos a imagem como não gravável
    image.flags.setflags(write=False)
    
    # Converte a imagem de BGR (padrão do OpenCV) para RGB (padrão do MediaPipe)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Processa a imagem e detecta os pontos do corpo
    results = pose.process(image_rgb)
    
    # Volta a imagem para o formato BGR para podermos desenhar nela com o OpenCV
    image.flags.setflags(write=True)
    image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

    # Verifica se os pontos do corpo (landmarks) foram detectados
    if results.pose_landmarks:
        # Desenha os landmarks na imagem para visualização
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
            mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
        )
        
        # Tenta obter os landmarks necessários para a análise da postura
        try:
            landmarks = results.pose_landmarks.landmark
            
            # Pega os pontos do ombro, orelha e quadril do lado esquerdo
            # Usamos o lado esquerdo como referência, mas poderia ser o direito
            shoulder_left = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            ear_left = landmarks[mp_pose.PoseLandmark.LEFT_EAR]
            hip_left = landmarks[mp_pose.PoseLandmark.LEFT_HIP]

            # Lógica de Postura: Calculamos o ângulo formado pelo ombro, orelha e quadril
            # Este ângulo ajuda a detectar se a pessoa está curvada para frente
            angle = calculate_angle(hip_left, shoulder_left, ear_left)

            # Define os limites para uma boa postura
            # Estes valores podem ser ajustados conforme necessário
            if 160 < angle < 185:
                posture_status = "Postura Boa"
                color = (0, 255, 0)  # Verde
            else:
                posture_status = "CORRIJA A POSTURA"
                color = (0, 0, 255)  # Vermelho

        except:
            posture_status = "Pontos nao visiveis"
            color = (0, 255, 255) # Amarelo

    # Exibe o status da postura na tela
    cv2.putText(image, posture_status, 
                (10, 30), # Posição do texto na tela
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)

    # Mostra a imagem resultante em uma janela
    cv2.imshow('Monitor de Postura com MediaPipe', image)

    # Encerra o programa se a tecla 'ESC' for pressionada
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Libera os recursos
cap.release()
cv2.destroyAllWindows()