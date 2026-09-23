import streamlit as st
import os
import time
import pandas as pd
import base64

from dotenv import load_dotenv

load_dotenv(override=True)


# =========================================================
# AUTH
# =========================================================

from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults


# =========================================================
# CONFIG
# =========================================================

from services.config.workout_config import EXERCISE_OPTIONS


# =========================================================
# UI
# =========================================================

from services.ui.style_loader import (
    load_css,
    inject_local_font,
    inject_webrtc_styles
)


# =========================================================
# DATABASE
# =========================================================

from services.persistence.exercise_repository import (
    init_db,
    get_users_exercises,
    add_exercise
)


# =========================================================
# WEBRTC
# =========================================================

from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode
)


# =========================================================
# VISION
# =========================================================

from services.vision.exercise_video_processor import (
    VideoProcessorClass
)


# =========================================================
# METRICS
# =========================================================

from services.tracking.metrics import (
    sync_metrics_update
)


# =========================================================
# GROQ
# =========================================================

from groq import Groq


# =========================================================
# COACHING
# =========================================================

from services.coaching.llm import (
    LLMCoach
)

from services.coaching.tts import (
    TextToSpeech
)

from services.coaching.voice_pipeline import (
    VoicePipeline,
    autoplay_audio
)


# =========================================================
# BACKGROUND
# =========================================================

def set_background():

    image_path = os.path.join(
        os.getcwd(),
        "static",
        "background.jpg"
    )

    with open(
        image_path,
        "rb"
    ) as image_file:

        encoded_image = base64.b64encode(
            image_file.read()
        ).decode()

    st.markdown(
        f"""
        <style>

        html,
        body,
        [data-testid="stAppViewContainer"] {{
            background-image:
                url("data:image/jpeg;base64,{encoded_image}") !important;

            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;
        }}

        [data-testid="stAppViewContainer"] > .main {{
            background: transparent !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        .stApp {{
            background: transparent !important;
        }}


        /* =================================================
           PRE-WORKOUT TEXT
           ================================================= */

        .pre-workout-black {{
            color: #000000 !important;
        }}

        .pre-workout-black * {{
            color: #000000 !important;
        }}


        /* =================================================
           SUMMARY EXERCISE
           ================================================= */

        .summary-exercise {{
            color: #000000 !important;
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 10px;
            margin-bottom: 20px;
        }}


        /* =================================================
           WORKOUT HISTORY TABLE
           ================================================= */

        [data-testid="stTable"] {{
            color: #000000 !important;
        }}

        [data-testid="stTable"] table {{
            color: #000000 !important;
            background-color: #ffffff !important;
        }}

        [data-testid="stTable"] thead {{
            color: #000000 !important;
            background-color: #ffffff !important;
        }}

        [data-testid="stTable"] tbody {{
            color: #000000 !important;
            background-color: #ffffff !important;
        }}

        [data-testid="stTable"] tr {{
            color: #000000 !important;
            background-color: #ffffff !important;
        }}

        [data-testid="stTable"] th {{
            color: #000000 !important;
            background-color: #ffffff !important;
            font-weight: 700 !important;
        }}

        [data-testid="stTable"] td {{
            color: #000000 !important;
            background-color: #ffffff !important;
        }}

        [data-testid="stTable"] th *,
        [data-testid="stTable"] td *,
        [data-testid="stTable"] tr *,
        [data-testid="stTable"] tbody *,
        [data-testid="stTable"] thead *,
        [data-testid="stTable"] table * {{
            color: #000000 !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# WORKOUT SUMMARY PAGE
# =========================================================

def render_workout_summary_page():

    st.title(
        "AI Real-time GYM Coach"
    )

    st.markdown(
        "#### Workout Summary"
    )

    st.divider()


    # =====================================================
    # GET SUMMARY DATA
    # =====================================================

    summary = st.session_state.get(
        "final_workout_summary",
        {}
    )


    if not summary:

        st.info(
            "No completed workout found."
        )


        if st.button(
            "🏋️ Start New Workout",
            width="stretch"
        ):

            st.session_state.current_page = "workout"

            st.session_state.workout_started = False

            st.session_state.workout_completed = False

            st.session_state.final_workout_summary = None

            st.session_state.audio_to_play = None

            st.session_state.coach_feedback = None

            st.session_state.final_voice_played = False

            st.rerun()


        return


    # =====================================================
    # SUMMARY VALUES
    # =====================================================

    exercise = summary.get(
        "exercise",
        "Unknown"
    )


    sets_completed = summary.get(
        "sets_completed",
        0
    )


    target_sets = summary.get(
        "target_sets",
        0
    )


    total_reps = summary.get(
        "total_reps",
        0
    )


    target_reps = summary.get(
        "target_reps",
        0
    )


    performance = summary.get(
        "performance",
        "incomplete"
    )


    # =====================================================
    # FINAL AI VOICE
    # =====================================================

    if (
        st.session_state.get("audio_to_play")
        and not st.session_state.get(
            "final_voice_played",
            False
        )
    ):

        print(
            "🔊 PLAYING FINAL WORKOUT AUDIO"
        )


        try:

            autoplay_audio(
                st.session_state.audio_to_play
            )


            st.session_state.final_voice_played = True


            print(
                "🔥 FINAL WORKOUT AUDIO PLAYED"
            )


        except Exception as e:

            print(
                "❌ FINAL AUDIO PLAY ERROR:",
                str(e)
            )


    # =====================================================
    # EXERCISE
    # =====================================================

    st.markdown(
        f"""
        <div class="summary-exercise">
            🏋️ Exercise: {exercise}
        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # SUMMARY METRICS
    # =====================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "🎯 Sets Completed",
            f"{sets_completed} / {target_sets}"
        )


    with col2:

        st.metric(
            "🔁 Total Reps",
            f"{total_reps} / {target_reps}"
        )


    with col3:

        st.metric(
            "💪 Performance",
            performance.capitalize()
        )


    st.divider()


    # =====================================================
    # WORKOUT HISTORY
    # =====================================================

    st.subheader(
        "📊 Workout History"
    )


    user_id = st.session_state.get(
        "user_id",
        0
    )


    if isinstance(user_id, int):

        history_rows = get_users_exercises(
            user_id
        )


        arr = []


        for row in history_rows:

            arr.append(
                {
                    "Exercise": row["exercise_name"],
                    "Date": row["created_at"],
                    "Reps": row["reps"],
                    "Sets": row["sets"],
                    "Time (sec)": row["time"]
                }
            )


        df = pd.DataFrame(arr)


        if not df.empty:

            # =================================================
            # DATE FORMAT
            # =================================================

            df["Date"] = pd.to_datetime(
                df["Date"]
            )


            # =================================================
            # NEWEST FIRST
            # =================================================

            df = df.sort_values(
                by="Date",
                ascending=False
            )


            # =================================================
            # DISPLAY DATE AND TIME
            # =================================================

            df["Date"] = df["Date"].dt.strftime(
                "%Y-%m-%d %H:%M:%S"
            )


            # =================================================
            # NUMBERING
            # =================================================

            df.insert(
                0,
                "#",
                range(
                    1,
                    len(df) + 1
                )
            )


            # =================================================
            # DISPLAY TABLE
            # =================================================

            st.table(
                df,
                border="horizontal"
            )


        else:

            st.info(
                "Aaj se koi workout history nahi hai."
            )


    else:

        st.info(
            "No workout history found."
        )


    st.divider()


    # =====================================================
    # START NEW WORKOUT
    # =====================================================

    if st.button(
        "🏋️ Start New Workout",
        width="stretch",
        key="start_new_workout_button"
    ):

        print(
            "🔥 START NEW WORKOUT CLICKED"
        )


        st.session_state.current_page = "workout"

        st.session_state.workout_started = False

        st.session_state.workout_completed = False

        st.session_state.final_workout_summary = None

        st.session_state.audio_to_play = None

        st.session_state.coach_feedback = None

        st.session_state.final_voice_played = False

        st.session_state.sets_completed = 0

        st.session_state.current_set_reps = 0

        st.session_state.reps = 0

        st.session_state.last_voice_rep = 0

        st.session_state.last_saved_sets_completed = 0

        st.session_state.last_notified_sets_completed = 0

        st.session_state.last_notified_workout_complete = False

        st.rerun()


# =========================================================
# MAIN
# =========================================================

def main():

    st.set_page_config(
        page_icon="🏋️‍♀️",
        page_title="AI Real-time GYM Coach",
        initial_sidebar_state="expanded",
        layout="centered"
    )


    # =====================================================
    # BASIC SETUP
    # =====================================================

    set_background()


    load_css(
        os.path.join(
            os.getcwd(),
            "static",
            "style.css"
        )
    )


    inject_local_font(
        os.path.join(
            os.getcwd(),
            "static",
            "AdobeClean.otf"
        ),
        "AdobeClean"
    )


    # =====================================================
    # DATABASE
    # =====================================================

    init_db()


    # =====================================================
    # LOGIN
    # =====================================================

    if not render_login_wall():

        return


    initial_session_defaults()


    # =====================================================
    # SESSION STATE
    # =====================================================

    if "audio_to_play" not in st.session_state:

        st.session_state.audio_to_play = None


    if "coach_feedback" not in st.session_state:

        st.session_state.coach_feedback = None


    if "sets_completed" not in st.session_state:

        st.session_state.sets_completed = 0


    if "current_set_reps" not in st.session_state:

        st.session_state.current_set_reps = 0


    if "workout_completed" not in st.session_state:

        st.session_state.workout_completed = False


    if "last_voice_rep" not in st.session_state:

        st.session_state.last_voice_rep = 0


    if "last_saved_sets_completed" not in st.session_state:

        st.session_state.last_saved_sets_completed = 0


    if "last_notified_sets_completed" not in st.session_state:

        st.session_state.last_notified_sets_completed = 0


    if "last_notified_workout_complete" not in st.session_state:

        st.session_state.last_notified_workout_complete = False


    if "final_workout_summary" not in st.session_state:

        st.session_state.final_workout_summary = None


    if "current_page" not in st.session_state:

        st.session_state.current_page = "workout"


    if "final_voice_played" not in st.session_state:

        st.session_state.final_voice_played = False


    # =====================================================
    # SUMMARY PAGE
    # =====================================================

    if (
        st.session_state.get(
            "current_page"
        ) == "summary"
    ):

        render_workout_summary_page()

        return


    # =====================================================
    # VOICE PIPELINE
    # =====================================================

    if "voice_pipeline" not in st.session_state:

        print(
            "🔥 STEP 1: Creating Voice Pipeline"
        )


        try:

            api_key = os.environ.get(
                "GROQ_API_KEY",
                ""
            )


            print(
                "API KEY LOADED:",
                bool(api_key)
            )


            print(
                "API KEY PREFIX:",
                api_key[:4]
                if api_key
                else "NONE"
            )


            print(
                "API KEY LENGTH:",
                len(api_key)
            )


            if (
                not api_key
                and hasattr(st, "secrets")
                and "GROQ_API_KEY" in st.secrets
            ):

                api_key = st.secrets[
                    "GROQ_API_KEY"
                ]


                print(
                    "🔥 STREAMLIT SECRETS API KEY FOUND"
                )


            if not api_key:

                print(
                    "❌ GROQ API KEY NOT FOUND"
                )

            else:

                print(
                    "🔥 GROQ API KEY FOUND"
                )


            groq_client = Groq(
                api_key=api_key
            )


            print(
                "🔥 GROQ CLIENT CREATED"
            )


            llm_coach = LLMCoach(
                groq_client
            )


            print(
                "🔥 LLM COACH CREATED"
            )


            tts = TextToSpeech()


            print(
                "🔥 TTS CREATED"
            )


            st.session_state.voice_pipeline = VoicePipeline(
                llm_coach,
                tts
            )


            print(
                "🔥🔥 VOICE PIPELINE CREATED SUCCESSFULLY 🔥🔥"
            )


        except Exception as e:

            print(
                "❌ VOICE PIPELINE INIT ERROR"
            )


            print(
                "ERROR TYPE:",
                type(e).__name__
            )


            print(
                "ERROR:",
                str(e)
            )


            st.session_state.voice_pipeline = None


    print(
        "🔥 VOICE PIPELINE STATUS:",
        st.session_state.get(
            "voice_pipeline"
        )
    )


    # =====================================================
    # WORKOUT STATE
    # =====================================================

    workout_started = st.session_state.get(
        "workout_started",
        False
    )


    # =====================================================
    # SIDEBAR
    # =====================================================

    with st.sidebar:

        st.title(
            "🏋️‍♂️ Apna AI Coach"
        )


        if st.session_state.get(
            "username"
        ):

            st.caption(
                f"👤 Login as {st.session_state.username}"
            )


        st.divider()


        # =================================================
        # BEFORE WORKOUT
        # =================================================

        if not workout_started:

            st.markdown(
                "### Workout Plan"
            )


            plan_exercise = st.selectbox(
                "Exercise",
                options=EXERCISE_OPTIONS,
                key="plan_exercise"
            )


            plan_sets = st.number_input(
                "Sets",
                min_value=0,
                max_value=50,
                key="plan_sets",
                step=1
            )


            plan_reps = st.number_input(
                "Reps per Set",
                min_value=0,
                max_value=50,
                key="plan_reps",
                step=1
            )


            st.markdown("")


            start_session_button = st.button(
                "Start Workout",
                width="stretch",
                key="start_session_button"
            )


            if start_session_button:

                print(
                    "🔥🔥 START WORKOUT BUTTON CLICKED 🔥🔥"
                )


                st.session_state.exercise_type = (
                    plan_exercise
                )


                st.session_state.target_sets = int(
                    plan_sets
                )


                st.session_state.reps_per_set = int(
                    plan_reps
                )


                st.session_state.reps = 0

                st.session_state.sets_completed = 0

                st.session_state.current_set_reps = 0

                st.session_state.last_voice_rep = 0

                st.session_state.workout_started = True

                st.session_state.workout_completed = False

                st.session_state.current_page = "workout"

                st.session_state.final_voice_played = False


                # Full workout timer
                st.session_state.workout_started_at = (
                    time.time()
                )


                st.session_state.set_cycle_started_at = (
                    time.time()
                )


                st.session_state.last_saved_sets_completed = 0

                st.session_state.last_notified_sets_completed = 0

                st.session_state.last_notified_workout_complete = False

                st.session_state.final_workout_summary = None

                st.session_state.coach_feedback = None

                st.session_state.audio_to_play = None


                # =========================================
                # START WORKOUT VOICE
                # =========================================

                if st.session_state.get(
                    "voice_pipeline"
                ):

                    print(
                        "🔥 ABOUT TO CALL START VOICE"
                    )


                    result = (
                        st.session_state.voice_pipeline.process_event(
                            event="workout_started",
                            exercise=plan_exercise,
                            metrics={}
                        )
                    )


                    print(
                        "🔥 START VOICE CALL FINISHED"
                    )


                    if result:

                        (
                            st.session_state.audio_to_play,
                            st.session_state.coach_feedback
                        ) = result


                        print(
                            "🔥 START AUDIO RECEIVED"
                        )


                    else:

                        print(
                            "❌ NO START AUDIO RECEIVED"
                        )


                else:

                    print(
                        "❌ VOICE PIPELINE IS NONE"
                    )


                st.rerun()


        # =================================================
        # DURING WORKOUT
        # =================================================

        else:

            exercise = st.session_state.get(
                "exercise_type",
                "Unknown"
            )


            target_sets = st.session_state.get(
                "target_sets",
                0
            )


            target_reps = st.session_state.get(
                "reps_per_set",
                0
            )


            completed_reps = st.session_state.get(
                "reps",
                0
            )


            completed_sets = st.session_state.get(
                "sets_completed",
                0
            )


            current_set_reps = st.session_state.get(
                "current_set_reps",
                0
            )


            # =============================================
            # WORKOUT PLAN
            # =============================================

            st.subheader(
                "Workout Plan"
            )


            st.info(
                f"🏋️ {exercise}"
            )


            st.markdown(
                f"🎯 **{target_sets} Sets × {target_reps} Reps**"
            )


            st.divider()


            # =============================================
            # LIVE WORKOUT
            # =============================================

            st.subheader(
                "📊 Live Workout"
            )


            st.metric(
                "Reps",
                completed_reps
            )


            st.metric(
                "Sets",
                f"{completed_sets} / {target_sets}"
            )


            st.metric(
                "Current Set Reps",
                f"{current_set_reps} / {target_reps}"
            )


            st.divider()


            # =============================================
            # EXERCISE METRICS
            # =============================================

            st.subheader(
                f"🏋️ {exercise} Metrics"
            )


            if exercise == "Squats":

                knee_angle = st.session_state.get(
                    "knee_angle",
                    0
                )


                back_angle = st.session_state.get(
                    "back_angle",
                    0
                )


                depth_status = st.session_state.get(
                    "depth_status",
                    "N/A"
                )


                st.metric(
                    "Knee Angle",
                    f"{knee_angle}°"
                )


                st.metric(
                    "Back Angle",
                    f"{back_angle}°"
                )


                st.metric(
                    "Depth Status",
                    depth_status
                )


            elif exercise == "Push-ups":

                elbow_angle = st.session_state.get(
                    "elbow_angle",
                    0
                )


                body_alignment = st.session_state.get(
                    "body_alignment",
                    "N/A"
                )


                hip_status = st.session_state.get(
                    "hip_status",
                    "N/A"
                )


                st.metric(
                    "Elbow Angle",
                    f"{elbow_angle}°"
                )


                st.metric(
                    "Body Alignment",
                    body_alignment
                )


                st.metric(
                    "Hip Position",
                    hip_status
                )


            elif exercise == "Biceps Curls (Dumbbell)":

                elbow_angle = st.session_state.get(
                    "elbow_angle",
                    0
                )


                shoulder_status = st.session_state.get(
                    "shoulder_status",
                    "N/A"
                )


                swing_status = st.session_state.get(
                    "swing_status",
                    "N/A"
                )


                st.metric(
                    "Elbow Angle",
                    f"{elbow_angle}°"
                )


                st.metric(
                    "Shoulder Stability",
                    shoulder_status
                )


                st.metric(
                    "Swing Detection",
                    swing_status
                )


            elif exercise == "Shoulder Press":

                elbow_angle = st.session_state.get(
                    "elbow_angle",
                    0
                )


                extension_status = st.session_state.get(
                    "extension_status",
                    "N/A"
                )


                back_arch_status = st.session_state.get(
                    "back_arch_status",
                    "N/A"
                )


                st.metric(
                    "Elbow Angle",
                    f"{elbow_angle}°"
                )


                st.metric(
                    "Arm Extension",
                    extension_status
                )


                st.metric(
                    "Back Arch",
                    back_arch_status
                )


            elif exercise == "Lunges":

                front_knee_angle = st.session_state.get(
                    "front_knee_angle",
                    0
                )


                torso_angle = st.session_state.get(
                    "torso_angle",
                    0
                )


                balance_status = st.session_state.get(
                    "balance_status",
                    "N/A"
                )


                st.metric(
                    "Front Knee Angle",
                    f"{front_knee_angle}°"
                )


                st.metric(
                    "Torso Angle",
                    f"{torso_angle}°"
                )


                st.metric(
                    "Balance Status",
                    balance_status
                )


            st.divider()


            # =============================================
            # END WORKOUT
            # =============================================

            end_session_button = st.button(
                "🔴 End Workout",
                key="end_session_button",
                width="stretch"
            )


            if end_session_button:

                print(
                    "🔥🔥 END WORKOUT BUTTON CLICKED 🔥🔥"
                )


                # =========================================
                # FINAL WORKOUT VALUES
                # =========================================

                final_exercise = st.session_state.get(
                    "exercise_type",
                    "Unknown"
                )


                final_sets = st.session_state.get(
                    "sets_completed",
                    0
                )


                final_reps = st.session_state.get(
                    "reps",
                    0
                )


                target_sets = st.session_state.get(
                    "target_sets",
                    0
                )


                target_reps = st.session_state.get(
                    "reps_per_set",
                    0
                )


                target_total_reps = (
                    target_sets * target_reps
                )


                # =========================================
                # WORKOUT TIME
                # =========================================

                workout_started_at = (
                    st.session_state.get(
                        "workout_started_at"
                    )
                )


                if workout_started_at:

                    workout_time = int(
                        time.time()
                        - workout_started_at
                    )

                else:

                    workout_time = 0


                # =========================================
                # PERFORMANCE
                # =========================================

                if (
                    final_sets >= target_sets
                    and final_reps >= target_total_reps
                    and target_total_reps > 0
                ):

                    performance = "excellent"

                elif (
                    final_sets > 0
                    or final_reps > 0
                ):

                    performance = "good"

                else:

                    performance = "incomplete"


                print(
                    "🏋️ FINAL EXERCISE:",
                    final_exercise
                )


                print(
                    "🏋️ FINAL SETS:",
                    final_sets
                )


                print(
                    "🏋️ FINAL REPS:",
                    final_reps
                )


                print(
                    "🏋️ WORKOUT TIME:",
                    workout_time
                )


                print(
                    "🏋️ PERFORMANCE:",
                    performance
                )


                # =========================================
                # SAVE WORKOUT TO DATABASE
                # =========================================

                user_id = st.session_state.get(
                    "user_id"
                )


                if user_id is not None:

                    try:

                        add_exercise(
                            user_id=user_id,
                            exercise_name=final_exercise,
                            reps=final_reps,
                            sets=final_sets,
                            time=workout_time
                        )


                        print(
                            "🔥🔥 WORKOUT SAVED TO DATABASE 🔥🔥"
                        )


                    except Exception as e:

                        print(
                            "❌ WORKOUT DATABASE SAVE ERROR:",
                            str(e)
                        )


                        st.error(
                            "Workout save nahi ho paya."
                        )


                else:

                    print(
                        "❌ USER ID NOT FOUND - WORKOUT NOT SAVED"
                    )


                    st.error(
                        "User ID nahi mila, workout save nahi hua."
                    )


                # =========================================
                # SAVE SUMMARY
                # =========================================

                st.session_state.final_workout_summary = {

                    "exercise": final_exercise,

                    "sets_completed": final_sets,

                    "target_sets": target_sets,

                    "total_reps": final_reps,

                    "target_reps": target_total_reps,

                    "performance": performance

                }


                # =========================================
                # FINAL AI VOICE
                # =========================================

                st.session_state.final_voice_played = False


                if st.session_state.get(
                    "voice_pipeline"
                ):

                    print(
                        "🔥🔥 CALLING FINAL WORKOUT VOICE"
                    )


                    result = (
                        st.session_state.voice_pipeline.process_event(
                            event="workout_completed",
                            exercise=final_exercise,
                            metrics={
                                "sets_completed": final_sets,
                                "total_reps": final_reps,
                                "target_sets": target_sets,
                                "reps_per_set": target_reps,
                                "performance": performance
                            }
                        )
                    )


                    print(
                        "🔥 FINAL VOICE RESULT:",
                        bool(result)
                    )


                    if result:

                        (
                            st.session_state.audio_to_play,
                            st.session_state.coach_feedback
                        ) = result


                        print(
                            "🔥🔥 FINAL AUDIO RECEIVED"
                        )


                    else:

                        print(
                            "❌ NO FINAL AUDIO RECEIVED"
                        )


                else:

                    print(
                        "❌ VOICE PIPELINE IS NONE"
                    )


                # =========================================
                # WORKOUT COMPLETE
                # =========================================

                st.session_state.workout_started = False

                st.session_state.workout_completed = True

                st.session_state.current_page = "summary"

                st.session_state.last_notified_workout_complete = True


                print(
                    "🔥🔥 WORKOUT MARKED AS COMPLETED"
                )


                print(
                    "🔥🔥 MOVING TO SUMMARY PAGE"
                )


                st.rerun()


    # =====================================================
    # MAIN PAGE
    # =====================================================

    workout_started = st.session_state.get(
        "workout_started",
        False
    )


    st.markdown(
        """
        <h1 style="color: #000000 !important;">
            🏋️‍♂️ AI Real-time GYM Trainer
        </h1>
        """,
        unsafe_allow_html=True
    )


    st.markdown(
        "#### Real-time pose detection with proactive AI voice coaching"
    )


    # =====================================================
    # AUDIO PLAYBACK
    # =====================================================

    if (
        workout_started
        and st.session_state.get(
            "audio_to_play"
        )
    ):

        print(
            "🔊 PLAYING AUDIO"
        )


        try:

            autoplay_audio(
                st.session_state.audio_to_play
            )


        except Exception as e:

            print(
                "❌ AUDIO PLAY ERROR:",
                str(e)
            )


    # =====================================================
    # DURING WORKOUT COACH TEXT
    # =====================================================

    if (
        workout_started
        and st.session_state.get(
            "coach_feedback"
        )
    ):

        st.markdown("")


        st.success(
            f"🤖 **Coach:** "
            f"{st.session_state.coach_feedback}"
        )


    # =====================================================
    # PRE-WORKOUT TRAINING OVERVIEW
    # =====================================================

    if not workout_started:

        selected_exercise = st.session_state.get(
            "plan_exercise",
            EXERCISE_OPTIONS[0]
        )


        selected_sets = st.session_state.get(
            "plan_sets",
            0
        )


        selected_reps = st.session_state.get(
            "plan_reps",
            0
        )


        total_target = (
            int(selected_sets)
            * int(selected_reps)
        )


        # =============================================
        # TODAY'S TRAINING
        # =============================================

        st.subheader(
            "🏋️ Today's Training"
        )


        st.markdown(
            f"🏋️ Exercise: **{selected_exercise}**"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "🎯 Sets",
                selected_sets
            )


        with col2:

            st.metric(
                "🔁 Reps / Set",
                selected_reps
            )


        with col3:

            st.metric(
                "📊 Total Target",
                total_target
            )


        st.divider()


        # =============================================
        # YOUR AI COACH WILL
        # =============================================

        st.subheader(
            "🤖 Your AI Coach Will"
        )


        st.markdown(
            "🎯 **Monitor your body position**"
        )


        st.markdown(
            "🎙️ **Give real-time voice corrections**"
        )


        st.markdown(
            "📈 **Track your reps and sets**"
        )


        st.markdown(
            "💪 **Analyze your workout performance**"
        )


        st.info(
            "💡 Set your workout from the sidebar, then click "
            "**Start Workout** to activate your AI Coach."
        )


    # =====================================================
    # CAMERA / POSE DETECTION
    # =====================================================

    if workout_started:

        context = webrtc_streamer(

            key="exercise-analysis",

            mode=WebRtcMode.SENDRECV,

            video_processor_factory=VideoProcessorClass,

            rtc_configuration={
                "iceServers": [
                    {
                        "urls": [
                            "stun:stun.l.google.com:19302"
                        ]
                    }
                ]
            },

            media_stream_constraints={
                "video": True,
                "audio": False
            },

            async_processing=True
        )


        sync_metrics_update(
            context
        )


        if context.state.playing:

            time.sleep(
                0.25
            )

            st.rerun()


        inject_webrtc_styles()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    main()

