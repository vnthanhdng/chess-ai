# Utility functions for chess AI

import chess
import chess.svg
import webbrowser
import tempfile
import os
from pathlib import Path


def render_board(board: chess.Board, output_file=None, open_browser=True, **kwargs):
    """
    Render a chess board as SVG and optionally display it in the browser.
    
    Args:
        board: chess.Board object to render
        output_file: Optional path to save the SVG file. If None, uses a temp file.
        open_browser: If True, opens the SVG in the default browser
        **kwargs: Additional arguments to pass to chess.svg.board() (e.g., size, arrows, fill, etc.)
    
    Returns:
        str: Path to the saved SVG file
    
    Example:
        >>> board = chess.Board()
        >>> render_board(board, size=400)
        >>> # With arrows and highlights
        >>> render_board(
        ...     board,
        ...     arrows=[chess.svg.Arrow(chess.E2, chess.E4)],
        ...     fill={chess.E4: "#cc0000cc"},
        ...     size=400
        ... )
    """
    # Set default size if not provided
    if 'size' not in kwargs:
        kwargs['size'] = 400
    
    # Generate the SVG
    svg_content = chess.svg.board(board, **kwargs)
    
    # Save to file
    if output_file is None:
        # Use a temporary file
        fd, output_file = tempfile.mkstemp(suffix='.svg', prefix='chess_board_')
        os.close(fd)
    else:
        # Ensure the directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG saved to: {output_file}")
    
    if open_browser:
        print("Opening in browser...")
        webbrowser.open(f'file://{os.path.abspath(output_file)}')
    
    return output_file


def save_board_image(board: chess.Board, output_file, format='svg', **kwargs):
    """
    Save a chess board as an image file.
    
    Args:
        board: chess.Board object to render
        output_file: Path to save the image file
        format: Image format ('svg', 'png', 'jpg'). For PNG/JPG, requires cairosvg.
        **kwargs: Additional arguments to pass to chess.svg.board()
    
    Returns:
        str: Path to the saved image file
    """
    if format == 'svg':
        return render_board(board, output_file=output_file, open_browser=False, **kwargs)
    else:
        try:
            import cairosvg
        except ImportError:
            raise ImportError(
                "cairosvg is required for PNG/JPG export. Install it with: pip install cairosvg"
            )
        
        # Generate SVG first
        if 'size' not in kwargs:
            kwargs['size'] = 400
        svg_content = chess.svg.board(board, **kwargs)
        
        # Convert to requested format
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'png':
            cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=output_file)
        elif format == 'jpg' or format == 'jpeg':
            cairosvg.svg2png(bytestring=svg_content.encode('utf-8'), write_to=output_file.replace('.jpg', '.png').replace('.jpeg', '.png'))
            # Note: JPG conversion would require PIL/Pillow for proper conversion
            print("Note: JPG format requires additional conversion. Saved as PNG instead.")
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'svg', 'png', or 'jpg'")
        
        print(f"Image saved to: {output_file}")
        return output_file

