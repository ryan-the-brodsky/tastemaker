"""
Video Processor for Interactive UX Audits

This module handles:
1. Video file validation and metadata extraction
2. Keyframe extraction using FFmpeg
3. Scene change detection
4. Temporal metric calculation between frames

Dependencies:
- FFmpeg must be installed on the system
- subprocess for FFmpeg commands
"""

import subprocess
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re


class VideoProcessorError(Exception):
    """Custom exception for video processing errors."""
    pass


class VideoProcessor:
    """
    Processes video files for UX interaction analysis.

    Extracts keyframes at regular intervals and on scene changes,
    enabling temporal analysis for Doherty Threshold compliance
    and interaction feedback timing.
    """

    # Supported video formats
    SUPPORTED_FORMATS = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}

    # Default extraction settings
    DEFAULT_FPS = 2  # Frames per second for regular extraction
    SCENE_THRESHOLD = 0.3  # Scene change detection threshold (0-1)
    MAX_FRAMES = 500  # Maximum frames to extract per video

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the video processor.

        Args:
            output_dir: Directory to store extracted frames.
                       If None, uses a temp directory.
        """
        self.output_dir = output_dir or tempfile.mkdtemp(prefix="tastemaker_frames_")
        self._ensure_ffmpeg_available()

    def _ensure_ffmpeg_available(self):
        """Check that FFmpeg is installed and accessible."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise VideoProcessorError("FFmpeg is not working properly")
        except FileNotFoundError:
            raise VideoProcessorError(
                "FFmpeg is not installed. Please install FFmpeg to use video auditing."
            )

    def validate_video(self, video_path: str) -> Dict[str, Any]:
        """
        Validate video file and extract metadata.

        Args:
            video_path: Path to the video file

        Returns:
            Dict with video metadata (duration, resolution, fps, codec)

        Raises:
            VideoProcessorError: If video is invalid or cannot be read
        """
        path = Path(video_path)

        if not path.exists():
            raise VideoProcessorError(f"Video file not found: {video_path}")

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise VideoProcessorError(
                f"Unsupported video format: {path.suffix}. "
                f"Supported: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # Use ffprobe to get video metadata
        try:
            result = subprocess.run([
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ], capture_output=True, text=True)

            if result.returncode != 0:
                raise VideoProcessorError(f"Cannot read video file: {result.stderr}")

            probe_data = json.loads(result.stdout)

            # Find video stream
            video_stream = None
            for stream in probe_data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break

            if not video_stream:
                raise VideoProcessorError("No video stream found in file")

            # Extract metadata
            duration_str = probe_data.get('format', {}).get('duration', '0')
            duration_ms = int(float(duration_str) * 1000)

            width = video_stream.get('width', 0)
            height = video_stream.get('height', 0)

            # Parse frame rate (can be "30/1" or "29.97")
            fps_str = video_stream.get('r_frame_rate', '30/1')
            if '/' in fps_str:
                num, denom = fps_str.split('/')
                fps = float(num) / float(denom)
            else:
                fps = float(fps_str)

            return {
                'duration_ms': duration_ms,
                'width': width,
                'height': height,
                'fps': round(fps, 2),
                'codec': video_stream.get('codec_name', 'unknown'),
                'total_frames': int(fps * (duration_ms / 1000))
            }

        except json.JSONDecodeError:
            raise VideoProcessorError("Failed to parse video metadata")
        except Exception as e:
            raise VideoProcessorError(f"Error reading video: {str(e)}")

    def extract_keyframes(
        self,
        video_path: str,
        recording_id: int,
        fps: Optional[float] = None,
        include_scene_changes: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extract keyframes from video using FFmpeg.

        Extracts frames at regular intervals and optionally on scene changes.

        Args:
            video_path: Path to video file
            recording_id: ID for organizing output
            fps: Frames per second for extraction (default: 2)
            include_scene_changes: Whether to also extract on scene changes

        Returns:
            List of frame metadata dicts with path and timestamp
        """
        fps = fps or self.DEFAULT_FPS

        # Create output directory for this recording
        frames_dir = Path(self.output_dir) / f"recording_{recording_id}"
        frames_dir.mkdir(parents=True, exist_ok=True)

        frames = []

        # 1. Extract frames at regular intervals
        regular_dir = frames_dir / "regular"
        regular_dir.mkdir(exist_ok=True)

        try:
            subprocess.run([
                'ffmpeg',
                '-i', video_path,
                '-vf', f'fps={fps}',
                '-frame_pts', '1',
                str(regular_dir / 'frame_%04d.png')
            ], capture_output=True, check=True)

            # Get timestamps for regular frames
            frames.extend(self._collect_frame_metadata(regular_dir, video_path, "regular"))

        except subprocess.CalledProcessError as e:
            raise VideoProcessorError(f"FFmpeg frame extraction failed: {e.stderr}")

        # 2. Extract on scene changes
        if include_scene_changes:
            scene_dir = frames_dir / "scenes"
            scene_dir.mkdir(exist_ok=True)

            try:
                subprocess.run([
                    'ffmpeg',
                    '-i', video_path,
                    '-vf', f"select='gt(scene,{self.SCENE_THRESHOLD})'",
                    '-vsync', 'vfr',
                    '-frame_pts', '1',
                    str(scene_dir / 'scene_%04d.png')
                ], capture_output=True, check=True)

                # Get timestamps for scene change frames
                scene_frames = self._collect_frame_metadata(scene_dir, video_path, "scene")

                # Merge, removing duplicates (within 100ms)
                frames = self._merge_frame_lists(frames, scene_frames)

            except subprocess.CalledProcessError:
                # Scene detection might fail for some videos, continue with regular frames
                pass

        # Sort by timestamp
        frames.sort(key=lambda f: f['timestamp_ms'])

        # Limit total frames
        if len(frames) > self.MAX_FRAMES:
            # Keep first and last frames, sample evenly from middle
            step = len(frames) // self.MAX_FRAMES
            frames = [frames[i] for i in range(0, len(frames), step)][:self.MAX_FRAMES]

        # Assign sequential frame numbers
        for i, frame in enumerate(frames):
            frame['frame_number'] = i

        return frames

    def _collect_frame_metadata(
        self,
        frame_dir: Path,
        video_path: str,
        frame_type: str
    ) -> List[Dict[str, Any]]:
        """Collect metadata for extracted frames."""
        frames = []

        # Get video duration for timestamp calculation
        metadata = self.validate_video(video_path)
        duration_ms = metadata['duration_ms']

        # Get all frame files sorted
        frame_files = sorted(frame_dir.glob('*.png'))

        if not frame_files:
            return frames

        # Calculate timestamps based on frame position
        for i, frame_path in enumerate(frame_files):
            # Estimate timestamp based on position
            # This is approximate - for precise timing, use frame PTS
            timestamp_ms = int((i / len(frame_files)) * duration_ms)

            frames.append({
                'path': str(frame_path),
                'timestamp_ms': timestamp_ms,
                'frame_type': frame_type,
            })

        return frames

    def _merge_frame_lists(
        self,
        list1: List[Dict],
        list2: List[Dict],
        dedup_threshold_ms: int = 100
    ) -> List[Dict]:
        """Merge two frame lists, removing duplicates within threshold."""
        merged = list1.copy()
        existing_timestamps = {f['timestamp_ms'] for f in list1}

        for frame in list2:
            ts = frame['timestamp_ms']
            # Check if there's already a frame within threshold
            is_duplicate = any(
                abs(ts - existing_ts) < dedup_threshold_ms
                for existing_ts in existing_timestamps
            )
            if not is_duplicate:
                merged.append(frame)
                existing_timestamps.add(ts)

        return merged

    def calculate_temporal_metrics(
        self,
        frames: List[Dict[str, Any]],
        extracted_values: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate temporal metrics between frames.

        Detects state transitions, loading indicators, and feedback timing
        for Doherty Threshold compliance checking.

        Args:
            frames: List of frame metadata with timestamps
            extracted_values: List of Claude-extracted values for each frame

        Returns:
            List of temporal metric dicts
        """
        if len(frames) != len(extracted_values):
            raise VideoProcessorError(
                f"Frame count ({len(frames)}) doesn't match extracted values ({len(extracted_values)})"
            )

        metrics = []

        for i in range(1, len(frames)):
            prev_frame = frames[i - 1]
            curr_frame = frames[i]
            prev_values = extracted_values[i - 1]
            curr_values = extracted_values[i]

            duration_ms = curr_frame['timestamp_ms'] - prev_frame['timestamp_ms']

            # Check for state transitions
            if self._detect_state_change(prev_values, curr_values):
                metrics.append({
                    'metric_type': 'state_transition_time',
                    'start_frame': i - 1,
                    'end_frame': i,
                    'duration_ms': duration_ms,
                    'details': {
                        'transition_type': self._identify_transition_type(prev_values, curr_values)
                    }
                })

            # Check for loading indicator appearance
            if self._detect_loading_start(prev_values, curr_values):
                metrics.append({
                    'metric_type': 'loading_indicator_delay',
                    'start_frame': i - 1,
                    'end_frame': i,
                    'duration_ms': duration_ms,
                    'details': {'loading_type': curr_values.get('loading_type', 'spinner')}
                })

            # Check for loading end (content appears)
            if self._detect_loading_end(prev_values, curr_values):
                metrics.append({
                    'metric_type': 'content_load_time',
                    'start_frame': i - 1,
                    'end_frame': i,
                    'duration_ms': duration_ms,
                    'details': {}
                })

            # Check for interaction feedback
            if self._detect_interaction_feedback(prev_values, curr_values):
                metrics.append({
                    'metric_type': 'interaction_feedback_time',
                    'start_frame': i - 1,
                    'end_frame': i,
                    'duration_ms': duration_ms,
                    'details': {
                        'feedback_type': curr_values.get('feedback_type', 'visual')
                    }
                })

        return metrics

    def _detect_state_change(self, prev: Dict, curr: Dict) -> bool:
        """Detect if there's a significant state change between frames."""
        # Check for URL/page changes
        if prev.get('current_url') != curr.get('current_url'):
            return True

        # Check for modal appearance/disappearance
        if prev.get('has_modal') != curr.get('has_modal'):
            return True

        # Check for form state changes
        if prev.get('form_state') != curr.get('form_state'):
            return True

        # Check for significant content changes
        prev_elements = set(prev.get('visible_elements', []))
        curr_elements = set(curr.get('visible_elements', []))
        if len(prev_elements.symmetric_difference(curr_elements)) > 3:
            return True

        return False

    def _detect_loading_start(self, prev: Dict, curr: Dict) -> bool:
        """Detect if a loading indicator appeared."""
        return (
            not prev.get('has_loading_indicator', False) and
            curr.get('has_loading_indicator', False)
        )

    def _detect_loading_end(self, prev: Dict, curr: Dict) -> bool:
        """Detect if loading completed (content appeared)."""
        return (
            prev.get('has_loading_indicator', False) and
            not curr.get('has_loading_indicator', False) and
            curr.get('has_content', False)
        )

    def _detect_interaction_feedback(self, prev: Dict, curr: Dict) -> bool:
        """Detect if there's interaction feedback (button state change, etc.)."""
        # Button state changes
        if prev.get('button_states') != curr.get('button_states'):
            return True

        # Error/success message appearance
        if not prev.get('has_feedback_message') and curr.get('has_feedback_message'):
            return True

        # Hover/focus state changes
        if prev.get('focused_element') != curr.get('focused_element'):
            return True

        return False

    def _identify_transition_type(self, prev: Dict, curr: Dict) -> str:
        """Identify the type of state transition."""
        if prev.get('current_url') != curr.get('current_url'):
            return 'navigation'
        if not prev.get('has_modal') and curr.get('has_modal'):
            return 'modal_open'
        if prev.get('has_modal') and not curr.get('has_modal'):
            return 'modal_close'
        if prev.get('form_state') != curr.get('form_state'):
            return 'form_state_change'
        return 'content_change'

    def cleanup(self, recording_id: Optional[int] = None):
        """
        Clean up extracted frames.

        Args:
            recording_id: If provided, only clean up frames for this recording.
                         If None, clean up entire output directory.
        """
        if recording_id:
            recording_dir = Path(self.output_dir) / f"recording_{recording_id}"
            if recording_dir.exists():
                shutil.rmtree(recording_dir)
        else:
            if Path(self.output_dir).exists():
                shutil.rmtree(self.output_dir)

    def get_frame_at_timestamp(
        self,
        video_path: str,
        timestamp_ms: int,
        output_path: str
    ) -> str:
        """
        Extract a single frame at a specific timestamp.

        Args:
            video_path: Path to video file
            timestamp_ms: Timestamp in milliseconds
            output_path: Where to save the frame

        Returns:
            Path to the extracted frame
        """
        timestamp_sec = timestamp_ms / 1000

        try:
            subprocess.run([
                'ffmpeg',
                '-ss', str(timestamp_sec),
                '-i', video_path,
                '-frames:v', '1',
                '-y',  # Overwrite if exists
                output_path
            ], capture_output=True, check=True)

            return output_path

        except subprocess.CalledProcessError as e:
            raise VideoProcessorError(f"Failed to extract frame at {timestamp_ms}ms: {e.stderr}")


# Convenience functions for common operations

def process_video_for_audit(
    video_path: str,
    recording_id: int,
    output_dir: Optional[str] = None
) -> Tuple[List[Dict], Dict]:
    """
    Process a video file for UX audit.

    Args:
        video_path: Path to video file
        recording_id: ID for organizing output
        output_dir: Optional output directory

    Returns:
        Tuple of (frames list, video metadata)
    """
    processor = VideoProcessor(output_dir)

    try:
        metadata = processor.validate_video(video_path)
        frames = processor.extract_keyframes(video_path, recording_id)

        return frames, metadata

    except VideoProcessorError:
        raise
    except Exception as e:
        raise VideoProcessorError(f"Video processing failed: {str(e)}")


def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed and accessible."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False
