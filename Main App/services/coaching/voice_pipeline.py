import time
import streamlit as st


print("🔥🔥🔥 THIS VOICE_PIPELINE FILE IS LOADED 🔥🔥🔥")


class VoicePipeline:

    def __init__(self, llm, tts):

        self.llm = llm
        self.tts = tts

        # =========================================================
        # VOICE TIMING
        # =========================================================

        self.last_spoken_at = 0
        self.last_form_spoken_at = 0
        self.last_no_pose_at = 0

        # =========================================================
        # REP / SET TRACKING
        # =========================================================

        self.last_rep = 0
        self.completed_sets = 0
        self.total_reps = 0

        # =========================================================
        # EVENT TRACKING
        # =========================================================

        self.last_event = None

        # =========================================================
        # FORM ISSUE TRACKING
        # =========================================================

        self.last_form_issue = None

    # =========================================================
    # FIND FORM ISSUE
    # =========================================================

    def _find_form_issue(self, exercise, metrics):

        if "issue" in metrics:
            return metrics["issue"]

        # ---------------------------------------------------------
        # SQUATS
        # ---------------------------------------------------------

        if exercise == "Squats":

            depth = metrics.get("depth_status", "")
            back_angle = metrics.get("back_angle", 180)

            if depth == "TOO HIGH":
                return (
                    "The user's squat is not deep enough. "
                    "Tell them to go a little deeper."
                )

            if isinstance(back_angle, (int, float)) and back_angle < 130:
                return (
                    "The user is leaning too far forward. "
                    "Tell them to keep their back straight."
                )

        # ---------------------------------------------------------
        # PUSH UPS
        # ---------------------------------------------------------

        elif exercise == "Push-ups":

            alignment = metrics.get("body_alignment", "")
            hip_status = metrics.get("hip_status", "")

            if alignment == "Poor Form":
                return (
                    "The user's body is not straight. "
                    "Tell them to maintain a straight body line."
                )

            if hip_status == "SAGGING":
                return (
                    "The user's hips are sagging. "
                    "Tell them to keep their body straight."
                )

            if hip_status == "PIKED UP":
                return (
                    "The user's hips are too high. "
                    "Tell them to lower their hips."
                )

        # ---------------------------------------------------------
        # BICEPS CURL
        # ---------------------------------------------------------

        elif exercise == "Biceps Curls (Dumbbell)":

            swing = metrics.get("swing_status", "")
            shoulder = metrics.get("shoulder_status", "")

            if swing == "SWINGING":
                return (
                    "The user is swinging their body. "
                    "Tell them to keep their body still and control the movement."
                )

            if shoulder == "ELBOW DRIFTING":
                return (
                    "The user's elbow is drifting away from their body. "
                    "Tell them to keep their elbow close to their side."
                )

        # ---------------------------------------------------------
        # SHOULDER PRESS
        # ---------------------------------------------------------

        elif exercise == "Shoulder Press":

            back_arch = metrics.get("back_arch_status", "")

            if back_arch == "Excessive Arch":
                return (
                    "The user is arching their lower back too much. "
                    "Tell them to brace their core."
                )

            if back_arch == "Slight Arch":
                return (
                    "A slight back arch is detected. "
                    "Tell the user to brace their core."
                )

        # ---------------------------------------------------------
        # LUNGES
        # ---------------------------------------------------------

        elif exercise == "Lunges":

            balance = metrics.get("balance_status", "")

            if balance == "OFF BALANCE":
                return (
                    "The user is losing balance. "
                    "Tell them to keep their feet stable."
                )

        return None

    # =========================================================
    # GENERATE VOICE
    # =========================================================

    def _generate_voice(self, event, prompt):

        try:

            print("🎤 CALLING LLM:", event)

            text = self.llm.give_feedback(
                event,
                prompt
            )

            print("🎤 LLM RESPONSE:", repr(text))

            if not text:
                return None

            print("🔊 CALLING TTS")

            voice = self.tts.speak(text)

            print(
                "🔊 TTS RETURNED:",
                len(voice) if voice else 0
            )

            if voice:

                self.last_spoken_at = time.time()
                self.last_event = event

                return voice, text

        except Exception as e:

            print("❌ VOICE ERROR:", type(e).__name__)
            print("❌ ERROR:", str(e))

        return None

    # =========================================================
    # PROCESS EVENTS
    # =========================================================

    def process_event(self, event, exercise, metrics):

        print("🔥 PROCESS EVENT CALLED:", event)

        now = time.time()

        # =====================================================
        # NO POSE DETECTED
        # =====================================================

        if event == "no_pose_detected":

            if now - self.last_no_pose_at < 7:
                return None

            result = self._generate_voice(
                event,
                (
                    "No pose is detected. "
                    "Tell the user clearly and professionally "
                    "to step into the camera frame."
                )
            )

            if result:

                self.last_no_pose_at = now
                self.last_form_issue = None

            return result

        # =====================================================
        # WORKOUT STARTED
        # =====================================================

        if event == "workout_started":

            # Reset workout counters
            self.last_rep = 0
            self.completed_sets = 0
            self.total_reps = 0
            self.last_form_issue = None

            return self._generate_voice(
                event,
                (
                    f"The user is starting a {exercise} workout. "
                    "Act like a professional gym trainer. "
                    "Give a very short introduction and mention "
                    "one important form or safety instruction "
                    "for this exercise. "
                    "Keep it natural and motivating. "
                    "Do not give a long explanation."
                )
            )

        # =====================================================
        # REP COMPLETED
        # =====================================================

        if event == "rep_completed":

            current_rep = metrics.get("reps", 0)

            if not isinstance(current_rep, int):

                try:
                    current_rep = int(current_rep)

                except:
                    return None

            # Only speak when a NEW rep is completed
            if current_rep <= self.last_rep:
                return None

            self.last_rep = current_rep

            # Track total reps
            self.total_reps += 1

            # Don't talk too frequently
            if now - self.last_spoken_at < 2:
                return None

            # -------------------------------------------------
            # FIRST REP
            # -------------------------------------------------

            if current_rep == 1:

                prompt = (
                    f"The user completed rep 1 of {exercise}. "
                    "Give very short professional trainer feedback. "
                    "Say the rep count and encourage them to continue."
                )

            # -------------------------------------------------
            # EVERY 5 REPS
            # -------------------------------------------------

            elif current_rep % 5 == 0:

                prompt = (
                    f"The user just completed rep {current_rep} "
                    f"of {exercise}. "
                    "Give short professional gym trainer feedback. "
                    "Mention the rep count and encourage good form. "
                    "Keep it under one sentence."
                )

            # -------------------------------------------------
            # OTHER REPS
            # -------------------------------------------------

            else:

                prompt = (
                    f"The user completed rep {current_rep} "
                    f"of {exercise}. "
                    "Give very short encouragement like a "
                    "professional gym trainer. "
                    "Mention the rep count naturally. "
                    "Do not speak too much."
                )

            return self._generate_voice(
                event,
                prompt
            )

        # =====================================================
        # SET COMPLETED
        # =====================================================

        if event == "set_completed":

            self.completed_sets += 1

            self.last_rep = 0
            self.last_form_issue = None

            set_reps = metrics.get(
                "reps",
                self.total_reps
            )

            return self._generate_voice(
                event,
                (
                    f"The user completed set {self.completed_sets} "
                    f"of their {exercise} workout. "
                    f"They completed approximately {set_reps} reps "
                    "in this set. "
                    "Congratulate them briefly, "
                    "tell them to take a short rest, "
                    "and prepare for the next set. "
                    "Keep it concise and motivating."
                )
            )

        # =====================================================
        # WORKOUT COMPLETED
        # =====================================================

        if event == "workout_completed":

            # Try to get actual values from metrics first
            total_sets = metrics.get(
                "sets_completed",
                self.completed_sets
            )

            total_reps = metrics.get(
                "total_reps",
                self.total_reps
            )

            # If total reps is provided through metrics,
            # use that value.
            if total_reps == 0:

                total_reps = metrics.get(
                    "reps",
                    0
                )

            # Performance information
            performance = metrics.get(
                "performance",
                metrics.get(
                    "performance_status",
                    "good"
                )
            )

            return self._generate_voice(
                event,
                (
                    f"The user has completed their {exercise} workout. "
                    f"They completed {total_sets} sets and "
                    f"{total_reps} total repetitions. "
                    f"Their overall performance was {performance}. "
                    "Act like a professional and encouraging gym trainer. "
                    "Congratulate the user, mention what they completed, "
                    "briefly comment on their performance, "
                    "and give a positive motivational message. "
                    "Encourage proper recovery after the workout. "
                    "Keep the feedback natural and under 3 sentences."
                )
            )

        # =====================================================
        # ONGOING FORM CHECK
        # =====================================================

        if event == "ongoing_form_check":

            issue = self._find_form_issue(
                exercise,
                metrics
            )

            # -------------------------------------------------
            # NO FORM PROBLEM
            # -------------------------------------------------

            if not issue:

                self.last_form_issue = None
                return None

            # -------------------------------------------------
            # SAME PROBLEM ALREADY REPORTED
            # -------------------------------------------------

            if issue == self.last_form_issue:
                return None

            # -------------------------------------------------
            # FORM VOICE COOLDOWN
            # -------------------------------------------------

            if now - self.last_form_spoken_at < 4:
                return None

            self.last_form_issue = issue

            result = self._generate_voice(
                event,
                (
                    "Act as a professional gym trainer. "
                    f"The user is doing {exercise}. "
                    f"Form issue detected: {issue} "
                    "Give ONE short, clear correction. "
                    "Do not explain too much."
                )
            )

            if result:

                self.last_form_spoken_at = now

            return result

        return None


# =============================================================
# AUTOPLAY AUDIO
# =============================================================

def autoplay_audio(audio_bytes):

    if not audio_bytes:
        return

    st.audio(
        audio_bytes,
        format="audio/mp3",
        autoplay=True
    )