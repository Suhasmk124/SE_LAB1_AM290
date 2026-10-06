import pygame
import random
import math
import array

from game.beat import (
    Note,
    LANES,
    LANE_KEYS,
    LANE_LABELS,
    LANE_COLORS
)


WIDTH, HEIGHT = 480, 640
FPS = 60
HIT_Y = HEIGHT - 80
HIT_WINDOW = 30
BG = (15, 10, 25)
LANE_W = WIDTH // LANES

# Task 3: BPM-synced spawning
BPM = 120
BEAT_INTERVAL = 60000 / BPM

# Task 2: Hold notes
HOLD_DURATION = 1000


class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption("Rhythm Tap")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(
            "monospace", 26, bold=True
        )

        self.big_font = pygame.font.SysFont(
            "monospace", 44, bold=True
        )

        # Task 1: hit sound
        self.hit_sound = self._create_hit_sound()

        self.reset()

    # ==================================================
    # TASK 1: HIT SOUND
    # ==================================================

    def _create_hit_sound(self):
        sample_rate = 44100
        duration = 0.10
        frequency = 700
        volume = 0.25

        samples = int(sample_rate * duration)

        buffer = array.array("h")

        for i in range(samples):

            envelope = 1.0 - (i / samples)

            sample = int(
                volume
                * 32767
                * envelope
                * math.sin(
                    2
                    * math.pi
                    * frequency
                    * i
                    / sample_rate
                )
            )

            buffer.append(sample)

        return pygame.mixer.Sound(
            buffer=buffer.tobytes()
        )

    # ==================================================
    # RESET
    # ==================================================

    def reset(self):

        self.notes = []

        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.misses = 0

        # ==============================================
        # TASK 4: GRADE COUNTERS
        # ==============================================

        self.perfect_count = 0
        self.great_count = 0
        self.ok_count = 0
        self.miss_count = 0

        self.speed = 5
        self.frame = 0

        self.feedback = []

        self.game_over = False

        # Task 3: BPM clock
        self.next_beat_time = (
            pygame.time.get_ticks()
        )

    # ==================================================
    # TASK 3: BPM NOTE SPAWNING
    # ==================================================

    def spawn_note(self):

        lane = random.randint(
            0,
            LANES - 1
        )

        # Task 2: 25% chance of hold note
        is_hold = random.random() < 0.25

        self.notes.append(
            Note(
                lane,
                y=-30,
                speed=self.speed,
                is_hold=is_hold,
                hold_duration=HOLD_DURATION
            )
        )

    # ==================================================
    # EVENTS
    # ==================================================

    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    self.reset()

                elif not self.game_over:

                    for i, key in enumerate(
                        LANE_KEYS
                    ):

                        if event.key == key:
                            self.process_tap(i)

        return True

    # ==================================================
    # PROCESS TAP
    # ==================================================

    def process_tap(self, lane):

        best = None
        best_dist = 9999

        for note in self.notes:

            if (
                note.lane == lane
                and not note.hit
                and not note.missed
                and not note.holding
            ):

                dist = abs(
                    note.y
                    + Note.HEIGHT // 2
                    - HIT_Y
                )

                if dist < best_dist:
                    best_dist = dist
                    best = note

        lane_x = (
            lane * LANE_W
            + LANE_W // 2
        )

        # ==================================================
        # SUCCESSFUL HIT
        # ==================================================

        if best and best_dist <= HIT_WINDOW:

            # ----------------------------------------------
            # HOLD NOTE
            # ----------------------------------------------

            if best.is_hold:

                best.holding = True

                best.hold_start_time = (
                    pygame.time.get_ticks()
                )

                self.feedback.append(
                    [
                        "HOLD",
                        (120, 200, 255),
                        40,
                        lane_x,
                        HIT_Y - 30
                    ]
                )

                return

            # ----------------------------------------------
            # NORMAL NOTE
            # ----------------------------------------------

            best.hit = True

            if best_dist < 8:

                grade = "PERFECT"
                pts = 300
                col = (255, 220, 0)

                # Task 4
                self.perfect_count += 1

            elif best_dist < 18:

                grade = "GREAT"
                pts = 200
                col = (100, 220, 100)

                # Task 4
                self.great_count += 1

            else:

                grade = "OK"
                pts = 100
                col = (180, 180, 255)

                # Task 4
                self.ok_count += 1

            # Task 1
            self.hit_sound.play()

            self.combo += 1

            self.max_combo = max(
                self.max_combo,
                self.combo
            )

            self.score += (
                pts
                * max(
                    1,
                    self.combo // 5
                )
            )

            self.feedback.append(
                [
                    grade,
                    col,
                    40,
                    lane_x,
                    HIT_Y - 30
                ]
            )

        # ==================================================
        # MISS FROM WRONG TAP
        # ==================================================

        else:

            self.combo = 0

            # Task 4
            self.miss_count += 1

            self.feedback.append(
                [
                    "MISS",
                    (220, 60, 60),
                    40,
                    lane_x,
                    HIT_Y - 30
                ]
            )

    # ==================================================
    # UPDATE
    # ==================================================

    def update(self):

        if self.game_over:
            return

        self.frame += 1

        current_time = (
            pygame.time.get_ticks()
        )

        # ==================================================
        # TASK 3: BPM-SYNCED SPAWNING
        # ==================================================

        while current_time >= self.next_beat_time:

            self.spawn_note()

            self.next_beat_time += (
                BEAT_INTERVAL
            )

        # Gradually increase note speed.
        # This does NOT control spawning.

        if self.frame % 600 == 0:

            self.speed = min(
                10,
                self.speed + 0.5
            )

        # ==================================================
        # UPDATE NOTES
        # ==================================================

        for note in self.notes:

            # ----------------------------------------------
            # TASK 2: HOLD NOTE
            # ----------------------------------------------

            if note.holding:

                keys = pygame.key.get_pressed()

                required_key = (
                    LANE_KEYS[note.lane]
                )

                # Released too early
                if not keys[required_key]:

                    note.holding = False
                    note.missed = True

                    self.misses += 1

                    # Task 4
                    self.miss_count += 1

                    self.combo = 0

                    lane_x = (
                        note.lane
                        * LANE_W
                        + LANE_W // 2
                    )

                    self.feedback.append(
                        [
                            "MISS",
                            (220, 60, 60),
                            40,
                            lane_x,
                            HIT_Y - 30
                        ]
                    )

                    continue

                elapsed = (
                    pygame.time.get_ticks()
                    - note.hold_start_time
                )

                # Successfully held for 1 second
                if elapsed >= note.hold_duration:

                    note.holding = False
                    note.hit = True

                    # Task 1
                    self.hit_sound.play()

                    # Count successful hold as OK
                    self.ok_count += 1

                    self.combo += 1

                    self.max_combo = max(
                        self.max_combo,
                        self.combo
                    )

                    self.score += (
                        300
                        * max(
                            1,
                            self.combo // 5
                        )
                    )

                    lane_x = (
                        note.lane
                        * LANE_W
                        + LANE_W // 2
                    )

                    self.feedback.append(
                        [
                            "HOLD OK",
                            (100, 255, 180),
                            40,
                            lane_x,
                            HIT_Y - 30
                        ]
                    )

                    continue

            # Move note
            note.update()

            # ----------------------------------------------
            # NOTE PASSED HIT ZONE
            # ----------------------------------------------

            if (
                not note.hit
                and not note.missed
                and not note.holding
                and note.y
                > HIT_Y
                + HIT_WINDOW
                + Note.HEIGHT
            ):

                note.missed = True

                self.misses += 1

                # Task 4
                self.miss_count += 1

                self.combo = 0

        # Remove completed/missed notes
        self.notes = [
            n
            for n in self.notes
            if not (
                n.hit
                or (
                    n.missed
                    and n.y > HEIGHT + 10
                )
            )
        ]

        # Feedback timer
        self.feedback = [
            [
                t,
                c,
                ttl - 1,
                x,
                y
            ]
            for t, c, ttl, x, y
            in self.feedback
            if ttl > 1
        ]

        if self.misses >= 15:
            self.game_over = True

    # ==================================================
    # TASK 4: ACCURACY
    # ==================================================

    def get_accuracy(self):

        total = (
            self.perfect_count
            + self.great_count
            + self.ok_count
            + self.miss_count
        )

        if total == 0:
            return 0.0

        successful = (
            self.perfect_count
            + self.great_count
            + self.ok_count
        )

        return (
            successful / total
        ) * 100

    # ==================================================
    # DRAW
    # ==================================================

    def draw(self):

        self.screen.fill(BG)

        # Lane dividers
        for i in range(LANES + 1):

            pygame.draw.line(
                self.screen,
                (40, 40, 60),
                (i * LANE_W, 0),
                (i * LANE_W, HEIGHT),
                1
            )

        # Hit line
        pygame.draw.line(
            self.screen,
            (80, 80, 100),
            (0, HIT_Y),
            (WIDTH, HIT_Y),
            2
        )

        # Lane buttons
        for i in range(LANES):

            lx = (
                i * LANE_W
                + LANE_W // 2
            )

            pygame.draw.rect(
                self.screen,
                LANE_COLORS[i],
                pygame.Rect(
                    lx - Note.WIDTH // 2,
                    HIT_Y - 12,
                    Note.WIDTH,
                    24
                ),
                border_radius=6
            )

            lbl = self.font.render(
                LANE_LABELS[i],
                True,
                (20, 20, 20)
            )

            self.screen.blit(
                lbl,
                (
                    lx
                    - lbl.get_width() // 2,
                    HIT_Y - 10
                )
            )

        # ==================================================
        # NOTES
        # ==================================================

        for note in self.notes:

            if note.hit:
                continue

            lx = (
                note.lane * LANE_W
                + LANE_W // 2
            )

            rect = note.get_rect(lx)

            if note.is_hold:

                pygame.draw.rect(
                    self.screen,
                    LANE_COLORS[note.lane],
                    rect,
                    border_radius=8
                )

                pygame.draw.line(
                    self.screen,
                    (255, 255, 255),
                    (
                        lx,
                        int(note.y)
                    ),
                    (
                        lx,
                        int(
                            note.y
                            + rect.height
                        )
                    ),
                    3
                )

            else:

                pygame.draw.rect(
                    self.screen,
                    LANE_COLORS[note.lane],
                    rect,
                    border_radius=5
                )

        # ==================================================
        # FEEDBACK
        # ==================================================

        for text, color, ttl, x, y in self.feedback:

            surf = self.font.render(
                text,
                True,
                color
            )

            alpha = min(
                255,
                ttl * 7
            )

            surf.set_alpha(alpha)

            self.screen.blit(
                surf,
                (
                    x
                    - surf.get_width() // 2,
                    y
                )
            )

        # ==================================================
        # NORMAL HUD
        # ==================================================

        sc = self.font.render(
            f"Score: {self.score}",
            True,
            (220, 220, 220)
        )

        co = self.font.render(
            f"Combo: {self.combo}x",
            True,
            (255, 220, 80)
        )

        mi = self.font.render(
            f"Misses: {self.misses}/15",
            True,
            (220, 100, 100)
        )

        self.screen.blit(sc, (10, 10))
        self.screen.blit(co, (10, 40))
        self.screen.blit(
            mi,
            (WIDTH - 170, 10)
        )

        # ==================================================
        # TASK 4: GRADE SUMMARY SCREEN
        # ==================================================

        if self.game_over:

            # Dark overlay
            overlay = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            overlay.fill(
                (0, 0, 0, 210)
            )

            self.screen.blit(
                overlay,
                (0, 0)
            )

            # Title
            title = self.big_font.render(
                "GRADE SUMMARY",
                True,
                (255, 220, 80)
            )

            self.screen.blit(
                title,
                (
                    WIDTH // 2
                    - title.get_width() // 2,
                    100
                )
            )

            # Counts
            perfect = self.font.render(
                f"PERFECT : {self.perfect_count}",
                True,
                (255, 220, 0)
            )

            great = self.font.render(
                f"GREAT   : {self.great_count}",
                True,
                (100, 220, 100)
            )

            ok = self.font.render(
                f"OK      : {self.ok_count}",
                True,
                (180, 180, 255)
            )

            miss = self.font.render(
                f"MISS    : {self.miss_count}",
                True,
                (220, 60, 60)
            )

            self.screen.blit(
                perfect,
                (100, 190)
            )

            self.screen.blit(
                great,
                (100, 230)
            )

            self.screen.blit(
                ok,
                (100, 270)
            )

            self.screen.blit(
                miss,
                (100, 310)
            )

            # Accuracy
            accuracy = self.get_accuracy()

            accuracy_text = self.font.render(
                f"Accuracy: {accuracy:.2f}%",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                accuracy_text,
                (
                    WIDTH // 2
                    - accuracy_text.get_width() // 2,
                    380
                )
            )

            # Score
            score_text = self.font.render(
                f"Final Score: {self.score}",
                True,
                (200, 200, 200)
            )

            self.screen.blit(
                score_text,
                (
                    WIDTH // 2
                    - score_text.get_width() // 2,
                    425
                )
            )

            # Max combo
            combo_text = self.font.render(
                f"Max Combo: {self.max_combo}x",
                True,
                (255, 220, 80)
            )

            self.screen.blit(
                combo_text,
                (
                    WIDTH // 2
                    - combo_text.get_width() // 2,
                    465
                )
            )

            # Restart
            restart = self.font.render(
                "Press R to Restart",
                True,
                (160, 160, 160)
            )

            self.screen.blit(
                restart,
                (
                    WIDTH // 2
                    - restart.get_width() // 2,
                    530
                )
            )

        pygame.display.flip()

    # ==================================================
    # RUN
    # ==================================================

    def run(self):

        running = True

        while running:

            running = self.handle_events()

            self.update()
            self.draw()

            self.clock.tick(FPS)

        pygame.quit()