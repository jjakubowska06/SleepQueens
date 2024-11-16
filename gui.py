import pygame
import sys
import yasa
import mne
import matplotlib.pyplot as plt
import numpy as np
import io

w = 1280
h = 720 

# pygame setup
pygame.init()
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Sleepy")
image = pygame.image.load("SleepQueen.png")

# Czcionka
font = pygame.font.Font(None, 100)
button_font = pygame.font.Font(None, 30)

title_text = font.render("SleepQueens", True, '#5f6796')

button_rect = pygame.Rect(w // 2 - 100, h // 2 + 200, 200, 60)
button_text = button_font.render("START", True, '#5f6796')

def start_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # Przechodzimy do gry

        screen.fill('#f4bcbc')
        # Rysowanie tła
        screen.blit(pygame.transform.scale(image, (w/3 + 50, h/3 + 50)), (700, h/2 - 200))

        # Rysowanie napisu
        screen.blit(title_text, (150,  h/2 - 100))

        # Rysowanie przycisku
        pygame.draw.rect(screen, '#5f6796', button_rect, width = 5)
        pygame.draw.rect(screen, '#fbcc20', button_rect.inflate(-10, -10))
        screen.blit(button_text, (button_rect.x + button_rect.width // 2 - button_text.get_width() // 2,
                                  button_rect.y + button_rect.height // 2 - button_text.get_height() // 2))

        # Aktualizacja ekranu
        pygame.display.flip()

def second_screen():
    input_text = ""  # Wprowadzony tekst
    is_typing = True  # Flaga, czy użytkownik wprowadza tekst

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if is_typing and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Przejście do następnego ekranu
                    print("Wprowadzony czas:", input_text)  # Debugowanie
                    return
                elif event.key == pygame.K_BACKSPACE:  # Usuwanie tekstu
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode  # Dodanie wprowadzonego znaku

        screen.fill('#f4bcbc')

        # Rysowanie tekstu informacyjnego
        font2 = pygame.font.Font(None, 80)
        screen.blit(font2.render("Welcome to SleepQueens Alarm App", True, '#5f6796'), (50, 50))
        screen.blit(font2.render("that helps you get up at the most", True, '#5f6796'), (50, 100))
        screen.blit(font2.render("optimal time for your health!", True, '#5f6796'), (50, 150))

        # Rysowanie pola tekstowego i wprowadzonego tekstu
        font3 = pygame.font.Font(None, 60)
        text_surface = font3.render('Enter the latest time you have to get up and press Enter', True, '#5f6796')
        screen.blit(text_surface, (50, 300))

        input_surface = font3.render(input_text, True, '#5f6796')
        pygame.draw.rect(screen, '#ffffff', pygame.Rect(50, 350, 800, 60))  # Pole tekstowe
        screen.blit(input_surface, (55, 355))

        # Aktualizacja ekranu
        pygame.display.flip()


def third_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # Przechodzimy do gry

        screen.fill('#f4bcbc')

        button_font = pygame.font.Font(None, 70)
        button_rect = pygame.Rect(w // 2 - 380, h // 2 - 150, 800, 240)
        button_text = button_font.render("ROZPOCZNIJ POMIAR", True, '#5f6796')

        # Rysowanie przycisku
        pygame.draw.rect(screen, '#5f6796', button_rect, width = 5)
        pygame.draw.rect(screen, '#fbcc20', button_rect.inflate(-10, -10))
        screen.blit(button_text, (button_rect.x + button_rect.width // 2 - button_text.get_width() // 2,
                                  button_rect.y + button_rect.height // 2 - button_text.get_height() // 2))

        # Aktualizacja ekranu
        pygame.display.flip()


start_screen()
second_screen()
third_screen()

# Główna pętla gry (tu wstaw swój kod gry)
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('#f4bcbc')  # Tło gry

    sig = mne.io.read_raw_edf('ST7112J0-PSG.edf', preload=True, verbose=True)
    sls = yasa.SleepStaging(sig, eeg_name="EEG Fpz-Cz", metadata=dict(age=21, male=False))
    hypno = sls.predict()

    cycles_stamps_smooth = []
    threshold = 35

    for i,state in enumerate(hypno):
        if len(hypno) == 1:
            continue

        # jesli poprzedni rem, a aktualny nie rem, to koniec cyklu
        if state != 'R' and hypno[i-1] == 'R':
            cycles_stamps_smooth.append(i)

        # smooth out hypno
        elif state == 'R':
            # check if previous state was R
            if hypno[i-1] == 'R':
                continue

        # threshold 15 min?
        elif 'R' in hypno[i-threshold:i-1]:
            cycles_stamps_smooth.pop(-1)


        hypno_num = hypno.copy()
        hypno_num[hypno=='W'] = 5
        hypno_num[hypno=='R'] = 4
        hypno_num[hypno=='N1'] = 3
        hypno_num[hypno=='N2'] = 2
        hypno_num[hypno=='N3'] = 1

        step_size=200
        rysuj_hypno = np.zeros(len(hypno))
        a = 0
        custom_labels = {1: 'N3', 2: 'N2', 3: 'N1', 4:'REM', 5:'WAKE'}

        for i in range(0, len(hypno_num), step_size):
            fig = plt.figure(figsize=(10,3))
            for stamp in cycles_stamps_smooth:
                if stamp <= i+step_size:
                    if stamp == cycles_stamps_smooth[-1]:
                        break
                    plt.vlines(stamp, 0, 5, color='#f5bebd')

        range_i = []
        rysuj_hypno[:i + step_size] = hypno_num[:i + step_size]
        plt.plot(rysuj_hypno, color = '#5e6697')
        plt.yticks(ticks=list(custom_labels.keys()), labels=list(custom_labels.values()))

        # Step 2: Save the plot to a BytesIO buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()  # Close the plot to free up memory

        # Step 3: Load the image from the buffer into pygame
        buf.seek(0)  # Rewind the buffer to the beginning
        plot_image = pygame.image.load(buf)

        # Step 4: Prepare for display in the pygame window
        plot_rect = plot_image.get_rect(center=(w // 2, h // 2))  # Position the plot in the center
        screen.blit(plot_image, plot_rect)  # Draw the image to the screen
        pygame.display.update()  # Update the pygame display

        # Step 5: Wait for a short time
        pygame.time.wait(500)  # Wait for 500ms before continuing


    # plt.show()
    
    pygame.display.flip()
