import pygame
import sys
import yasa
import mne
import matplotlib.pyplot as plt
import numpy as np
import io
import re

# Rozmiar okna
w, h = 1280, 720

# pygame setup
pygame.init()
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("CATApp")
image = pygame.image.load("SleepQueen.png")

# Czcionki
font = pygame.font.Font(None, 100)
font_m = pygame.font.Font(None, 80)
font_2m = pygame.font.Font(None, 60)
button_font = pygame.font.Font(None, 30)

# Napisy i przyciski
title_text = font.render("CATApp", True, '#5f6796')
button_rect = pygame.Rect(w // 2 - 100, h // 2 + 200, 200, 60)
button_text = button_font.render("START", True, '#5f6796')

# Funkcja uniwersalnego przycisku
def draw_button(rect, text_surface, text_color, bg_color, border_color):
    pygame.draw.rect(screen, border_color, rect, width=5)
    pygame.draw.rect(screen, bg_color, rect.inflate(-10, -10))
    screen.blit(text_surface, (rect.x + rect.width // 2 - text_surface.get_width() // 2,
                                rect.y + rect.height // 2 - text_surface.get_height() // 2))

# Ekran startowy
def start_screen():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # Przejście do następnego ekranu

        screen.fill('#f4bcbc')
        screen.blit(pygame.transform.scale(image, (w // 3 + 50, h // 3 + 50)), (700, h / 2 - 180))
        screen.blit(title_text, (100, h / 2 - 150))
        screen.blit(font_2m.render('Custom Alarm Technology', True, '#5f6796'), (100, h/2 - 50))
        font_2m.set_italic(True)
        screen.blit(font_2m.render('by SleepQueens', True, '#5f6796'), (100, h/2))
        draw_button(button_rect, button_text, '#5f6796', '#fbcc20', '#5f6796')

        pygame.display.flip()

# Drugi ekran z wprowadzaniem czasu
def second_screen():
    input_text = ""  # Wprowadzony tekst
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Walidacja i przejście dalej
                    if re.match(r"^\d{2}:\d{2}$", input_text):  # Sprawdzenie formatu HH:MM
                        hours, minutes = map(int, input_text.split(":"))
                        if 0 <= hours < 24 and 0 <= minutes < 60:
                            print("Wprowadzony czas:", input_text)
                            return
                    print("Niepoprawny format czasu! Wprowadź w formacie HH:MM.")
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        screen.fill('#f4bcbc')
        font2 = pygame.font.Font(None, 80)
        screen.blit(font2.render("Welcome to CATApp that helps you", True, '#5f6796'), (150, 100))
        screen.blit(font2.render("get up at the most optimal time", True, '#5f6796'), (200, 180))
        font3 = pygame.font.Font(None, 60)
        text_surface = font3.render('What is the latest time you have to get up?', True, '#5f6796')
        screen.blit(text_surface, (50, 350))

        pygame.draw.rect(screen, '#ffffff', pygame.Rect(100, 400, 750, 60))
        input_surface = font3.render(input_text, True, '#5f6796')
        screen.blit(input_surface, (400, 410))
        font4 = pygame.font.Font(None, 40)
        font4.set_italic(True)
        screen.blit(font4.render("Press Enter", True, '#5f6796'), (380, 470))

        pygame.display.flip()

# Trzeci ekran z przyciskiem pomiaru
def third_screen():
    while True:
        button_rect = pygame.Rect(w // 2 - 380, h // 2 - 150, 800, 240)
        button_font = pygame.font.Font(None, 70)
        button_text = button_font.render("START MEASUREMENT", True, '#5f6796')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # Rozpoczęcie gry

        screen.fill('#f4bcbc')
        draw_button(button_rect, button_text, '#5f6796', '#fbcc20', '#5f6796')
        pygame.display.flip()

# Rysowanie hipnogramu
def render_hypnogram_step_by_step(hypno, screen, step_size=20, threshold = 35):

    # smoothing cycles
    cycles_stamps_smooth = []

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

    t = np.arange(0, len(hypno)) / 120

    sleep_stage_map = {'W': 5, 'R': 4, 'N1': 3, 'N2': 2, 'N3': 1}
    hypno_num = [sleep_stage_map[state] for state in hypno]

    # Inicjalizacja pustego hipnogramu
    rysuj_hypno = np.zeros(len(hypno_num))
    custom_labels = {1: 'N3', 2: 'N2', 3: 'N1', 4: 'REM', 5: 'WAKE'}

    for i in range(0, len(hypno_num), step_size):
        # Zaktualizowanie hipnogramu krok po kroku
        rysuj_hypno[:i + step_size] = hypno_num[:i + step_size]

        # Rysowanie wykresu
        plt.figure(figsize=(10, 3))

        # cycles
        for j, stamp in enumerate(cycles_stamps_smooth):
            if j == 5:
                plt.vlines(stamp, 0, 6, color='#f5bebd', linewidth=3)
                break
            if stamp <= i+step_size:
                if stamp == cycles_stamps_smooth[-1]:
                    break
                plt.vlines(stamp, 0, 6, color='#f5bebd', linewidth=3)

        plt.plot(rysuj_hypno, color='#5e6697', label="Hypnogram")
        plt.yticks(list(custom_labels.keys()), list(custom_labels.values()))
        plt.ylim(0.5, 5.5)  # Ustawienie zakresu Y dla czytelności

        # axis !!!
        max_sample = len(hypno)
        samples_per_hour = 120
        hour_ticks = np.arange(0, max_sample + 1, samples_per_hour)  # Hour ticks
        hour_labels = [f'{tick // samples_per_hour:.1f}h' for tick in hour_ticks]  # Convert ticks to hours
        plt.xticks(ticks=hour_ticks, labels=hour_labels)

        plt.legend()
        plt.grid(axis='x', linestyle='--', alpha=0.5)

        # Zapisanie aktualnego stanu do bufora
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)
        plot_image = pygame.image.load(buf)

        # Wyświetlenie wykresu w oknie pygame
        screen.fill('#f4bcbc')
        screen.blit(plot_image, plot_image.get_rect(center=(w // 2, h // 2)))
        pygame.display.flip()

        # Opóźnienie, aby symulować krokowy przebieg
        pygame.time.wait(10)  # 500ms przerwy między krokami

    return cycles_stamps_smooth


def alarm_animation():
    # Załaduj obraz budzika
    alarm_image = pygame.image.load("budzik.png")
    
    # Zmień rozmiar obrazka (np. do 50% oryginalnej wielkości)
    scaled_width = alarm_image.get_width() // 2
    scaled_height = alarm_image.get_height() // 2
    alarm_image = pygame.transform.scale(alarm_image, (scaled_width, scaled_height))

    alarm_rect = alarm_image.get_rect(center=(w // 2, h // 2))

    # Załaduj dźwięk dzwonka
    pygame.mixer.init()
    alarm_sound = pygame.mixer.Sound("Budzik.mp3")
    alarm_sound.play(-1)  # Odtwarzanie w pętli

    start_time = pygame.time.get_ticks()  # Zapisz czas początkowy
    duration = 5000  # Animacja trwa 5 sekund

    while True:
        current_time = pygame.time.get_ticks()
        if current_time - start_time > duration:
            break  # Zakończ animację po upływie 5 sekund

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                alarm_sound.stop()
                pygame.quit()
                sys.exit()

        # Efekt trzęsienia budzika
        offset_x = np.random.randint(-10, 10)
        offset_y = np.random.randint(-10, 10)
        screen.fill('#f4bcbc')
        screen.blit(alarm_image, alarm_rect.move(offset_x, offset_y))

        # Aktualizacja ekranu
        pygame.display.flip()
        pygame.time.wait(50)  # Krótkie opóźnienie dla efektu animacji

    # Zatrzymaj dźwięk po zakończeniu animacji
    alarm_sound.stop()


def sleep_statistic(hypno, cycles_stamps_smooth, screen):
    if len(hypno) <= 1:
        return  # Jeśli hypno jest za krótkie, nie wykonuj dalszych operacji

    hypno = hypno.tolist()  # Konwersja do listy, jeśli to potrzebne

    total_sleep_time = sum(1 for state in hypno if state != 'W') / 120

    # Oblicz czas trwania cykli w godzinach
    if cycles_stamps_smooth and cycles_stamps_smooth[0] != 0:
        cycles_stamps_smooth.insert(0, 0)

    # Oblicz długość każdego cyklu w minutach i przelicz na godziny
    cycle_durations_hours = [
        (cycles_stamps_smooth[i] - cycles_stamps_smooth[i - 1]) / 120
        for i in range(1, len(cycles_stamps_smooth))
    ]

    # Tworzenie wykresu
    plt.figure(figsize=(6, 4))
    if cycle_durations_hours:
        plt.scatter(range(1, len(cycle_durations_hours) + 1), cycle_durations_hours, color='#5e6697', label='Cycle duration (h)')
        plt.plot(range(1, len(cycle_durations_hours) + 1), cycle_durations_hours, color='#f4bcbc', alpha=0.5)
    plt.xticks(range(1, len(cycle_durations_hours) + 1))
    plt.xlabel('Cycle number')
    plt.ylabel('Cycle duration (h)')
    plt.grid(True)
    plt.legend()

    # Zapisanie wykresu do bufora
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    # Załaduj obraz do pygame
    plot_image = pygame.image.load(buf)

    # Wyświetl statystyki i wykres na ekranie pygame
    stat_font = pygame.font.Font(None, 60)
    text_lines = [
        f"Amount of cycles: {len(cycles_stamps_smooth)-1}",
        f"Sleep duration: {total_sleep_time:.2f} hours"
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill('#f4bcbc')

        # Rysujemy tekst statystyk
        y_offset = 50
        for line in text_lines:
            stat_text = stat_font.render(line, True, '#5f6796')
            screen.blit(stat_text, (w // 2 - stat_text.get_width() // 2, y_offset))
            y_offset += 80

        # Rysujemy wykres
        screen.blit(plot_image, plot_image.get_rect(center=(w // 2, h // 2 + 100)))

        pygame.display.flip()

    

def game_loop():
    try:
        # Wczytanie sygnału EEG
        sig = mne.io.read_raw_edf('ST7112J0-PSG.edf', preload=True, verbose=True)
        sls = yasa.SleepStaging(sig, eeg_name="EEG Fpz-Cz", metadata=dict(age=21, male=False))
        hypno = sls.predict()


        cycles_stamps_smooth = render_hypnogram_step_by_step(hypno, screen, step_size=20)

        # Animacja alarmu
        alarm_animation()

        # Wyświetlenie statystyk
        sleep_statistic(hypno, cycles_stamps_smooth,screen)


        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
    except FileNotFoundError:
        print("EDF file not found. Please make sure 'ST7112J0-PSG.edf' is in the directory.")
        pygame.quit()
        sys.exit()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()


# Uruchomienie gry
start_screen()
second_screen()
third_screen()
game_loop()
