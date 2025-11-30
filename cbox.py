import svgwrite
import argparse

def create_cbox_template(length_in, width_in, height_in, thickness,
                         labels,
                         folds,
                         filename,
                         ):
    """
    Creates an SVG template for a seamless cardboard box.

    Args:
        length_in (float): Interior length of the box (mm).
        width_in (float): Interior width of the box (mm).
        height_in (float): Interior height of the box (mm).
        thickness (float): Thickness of the cardboard (mm).
        filename (str): Output filename.
    """

    # --- Geometric Calculations ---
    peel_height = 2 * thickness
    flap_height = 10  # Standard glue flap height
    wall_thickness = 2 * thickness

    # Base Dimensions
    base_l = length_in + (2 * wall_thickness)
    base_w = width_in + (2 * wall_thickness)

    # Side 2 (Short Side) Profile Heights - FOR CONTINUOUS STRIP
    # User requested removing "tabs" (flaps) from outer edges of the base strip.
    # New Stack: Outer(H) + Peel(P) + Inner(H)
    # We remove the glue flap and the peel strip connecting it.
    side_2_strip_height_component = height_in + peel_height + height_in

    # Strip Dimensions (Base + 2 Short Sides)
    strip_width = base_l
    strip_height = 4 * height_in + 2 * peel_height + 2 * thickness + base_w
    print(f"{strip_height=}")

    # Side 1 (Long Side) Dimensions - SEPARATE PIECES
    # These retain the flaps (Type C typically needs them).
    side_1_outer_width = base_w + (2 * wall_thickness)
    side_1_inner_width = width_in
    # Side 1 Stack: Outer(H) + Peel(P) + Inner(H) + Peel(P) + Flap(F)
    side_1_stack_height = height_in + peel_height + height_in + peel_height + flap_height

    # --- SVG Setup ---
    padding = 5

    # Calculate Total Canvas Size
    # Layout: [Strip] [Padding] [Side 1 Top]
    #                           [Side 1 Bottom]
    total_width = padding + strip_width + padding + side_1_outer_width + padding
    right_col_height = (side_1_stack_height * 2) + padding
    total_height = max(strip_height, right_col_height) + (2 * padding)

    dwg = svgwrite.Drawing(
        filename,
        profile='tiny',
        size=(f"{total_width}mm", f"{total_height}mm"),
        )
    dwg.viewbox(0, 0, total_width, total_height)

    # Define styles
    cut_args = {'stroke': 'black', 'stroke_width': '0.4mm', 'fill': 'none'}
    peel_args = {'stroke': 'red', 'stroke_width': '0.2mm', 'fill': 'none'}
    fold_args = {'stroke': 'blue', 'stroke_width': '0.2mm',
                 #'fill': 'none',
                 'stroke_dasharray': '1.0mm,0.6mm',
                 }

    def add_label(text, x, y):
        dwg.add(dwg.text(text, insert=(x, y), fill='blue', font_size='1mm', font_family='sans-serif'))

    # --- Draw Continuous Strip (Side 2 Top + Base + Side 2 Bottom) ---
    strip_x = padding
    current_y = padding

    #base_height = 4 * height_in + 2 * peel_height + 2 * thickness + base_w
    label_y_offset = 2 * height_in + peel_height + thickness + 15
    if labels:
        add_label(f"Main Body (outside dims {strip_height:.1f} x {length_in} mm)", strip_x + 5, current_y + label_y_offset)

    # Calculate Y positions for all horizontal lines in the strip
    # 1. Top Side (Inverted: Inner -> Peel -> Outer)
    # Note: We removed Flap and the Peel connecting to it.
    fold_lines_y = []
    peel_lines_y = []
    #fold_lines_y.append(current_y)

    # Side
    peel_lines_y.append(current_y + height_in)
    peel_lines_y.append(current_y + 1 * height_in + 1 * peel_height)
    peel_lines_y.append(current_y + 2 * height_in + 1 * peel_height)

    # Base
    base_top =          current_y + 2 * height_in + 1 * peel_height + thickness
    peel_lines_y.append(base_top)
    base_bottom =       current_y + 2 * height_in + 1 * peel_height + thickness + base_w
    peel_lines_y.append(base_bottom)
    # Side
    peel_lines_y.append(current_y + 2 * height_in + 1 * peel_height + 2 * thickness +
                        base_w)
    peel_lines_y.append(current_y + 3 * height_in + 1 * peel_height + 2 * thickness +
                        base_w)
    peel_lines_y.append(current_y + 3 * height_in + 2 * peel_height + 2 * thickness +
                        base_w)
    # Draw Internal Lines (Peel/Score)
    for y in peel_lines_y:
        dwg.add(dwg.line(start=(strip_x, y),
                         end=(strip_x + base_l, y),
                         **peel_args)
                )
    if folds:
        for y in fold_lines_y:
            dwg.add(dwg.line(start=(strip_x, y),
                             end=(strip_x + base_l, y),
                             **fold_args)
                    )

    # Draw Outer Box
    dwg.add(dwg.rect(insert=(strip_x, current_y),
                         size=(strip_width, strip_height), **cut_args))
    # Draw Vertical folds (where the sides meet the base strip
    if folds:
        dwg.add(dwg.line(start=(strip_x + peel_height, base_top),
                         end=  (strip_x + peel_height, base_bottom),
                         **fold_args)
                    )
        dwg.add(dwg.line(start=(strip_x + peel_height + length_in, base_top),
                         end=  (strip_x + peel_height + length_in, base_bottom),
                         **fold_args)
                    )

    # --- Draw Side 1 (Long Sides) x2 ---
    # These remain separate pieces with flaps
    side1_x_start = strip_x + strip_width + padding
    current_y = padding

    side_height = 2 * height_in + 2 * peel_height + flap_height
    for i in range(2):

        y_cursor = current_y

        # Calculate X offsets relative to this column
        outer_w = side_1_outer_width
        inner_w = side_1_inner_width

        x_outer_left = side1_x_start
        x_inner_left = side1_x_start + (outer_w - inner_w) / 2

        x_outer_right = side1_x_start + outer_w
        x_inner_right = x_inner_left + inner_w

        if labels:
            add_label(f"Side Panel (outside dims {side_height:.1f} x {side_1_outer_width} mm) #{i+1}",
                      x_inner_left + 5, current_y + 15)

        # 1. Cut Outline

        # Top
        dwg.add(dwg.line(start=(x_inner_left, y_cursor),
                         end=(x_inner_right, y_cursor),
                         **cut_args),
                )
        # TL Chamfer
        dwg.add(dwg.line(start=(x_inner_left - peel_height, y_cursor + 1),
                         end=(x_inner_left, y_cursor),
                         **cut_args),
                )
        # TR Chamfer
        dwg.add(dwg.line(start=(x_inner_right + peel_height, y_cursor + 1),
                         end=(x_inner_right, y_cursor),
                         **cut_args),
                )
        # Left Side - Upper left edge
        dwg.add(dwg.line(start=(x_inner_left - peel_height, y_cursor + 1),
                         end=  (x_inner_left - peel_height, y_cursor + height_in),
                         **cut_args),
                )
        # Left Side - Upper Side Bottom Edge
        dwg.add(dwg.line(start=(x_inner_left, y_cursor + height_in),
                         end=  (x_inner_left - peel_height, y_cursor + height_in),
                         **cut_args),
                )
        # Left Side - Middle Peel Chamfer
        dwg.add(dwg.line(start=(x_inner_left,
                                y_cursor + height_in),
                         end=(  x_inner_left - peel_height,
                                y_cursor + height_in + peel_height),
                         **cut_args),
                )
        # Left Side - Lower Side Top Edge
        dwg.add(dwg.line(start=(x_inner_left - peel_height,
                                y_cursor + height_in + peel_height),
                         end=(x_outer_left,
                              y_cursor + height_in + peel_height),
                         **cut_args),
                )
        # Left Side - Lower Side Edge
        dwg.add(dwg.line(start=(x_outer_left,
                                y_cursor + height_in + peel_height),
                         end=(  x_outer_left,
                                y_cursor + 2 * height_in + 2 * peel_height - 1),
                         **cut_args),
                )
        # Left Side - Lower Side Bottom Edge
        dwg.add(dwg.line(start=(x_outer_left,
                                y_cursor + 2 * height_in + 2 * peel_height - 1),
                         end=(  x_inner_left - peel_height,
                                y_cursor + 2 * height_in + 2 * peel_height),
                         **cut_args),
                )
        # Left Side - Bottom Flap Left Chamfer
        dwg.add(dwg.line(start=(x_inner_left - peel_height,
                                y_cursor + 2 * height_in + 2 * peel_height),
                         end=(  x_inner_left,
                                y_cursor + 2 * height_in + 2 * peel_height + flap_height),
                         **cut_args),
                )


        # Right Side - Upper Right Edge
        dwg.add(dwg.line(start=(x_inner_right + peel_height, y_cursor + 1),
                         end=  (x_inner_right + peel_height, y_cursor + height_in),
                         **cut_args),
                )
        # Right Side - Upper Side Bottom Edge
        dwg.add(dwg.line(start=(x_inner_right, y_cursor + height_in),
                         end=(x_inner_right + peel_height, y_cursor + height_in),
                         **cut_args),
                )
        # Right Side - Middle Peel Chamfer
        dwg.add(dwg.line(start=(x_inner_right,
                                y_cursor + height_in),
                         end=(  x_inner_right + peel_height,
                                y_cursor + height_in + peel_height),
                         **cut_args),
                )
        # Right Side - Lower Side Top Edge
        dwg.add(dwg.line(start=(x_inner_right + peel_height,
                                y_cursor + height_in + peel_height),
                         end=(x_outer_right,
                              y_cursor + height_in + peel_height),
                         **cut_args),
                )
        # Right Side - Lower Side Edge
        dwg.add(dwg.line(start=(x_outer_right,
                                y_cursor + height_in + peel_height),
                         end=(  x_outer_right,
                                y_cursor + 2 * height_in + 2 * peel_height - 1),
                         **cut_args),
                )
        # Right Side - Lower Side Bottom Edge
        dwg.add(dwg.line(start=(x_outer_right,
                                y_cursor + 2 * height_in + 2 * peel_height - 1),
                         end=(  x_inner_right + peel_height,
                                y_cursor + 2 * height_in + 2 * peel_height),
                         **cut_args),
                )
        # Right Side - Bottom Flap Right Chamfer
        dwg.add(dwg.line(start=(x_inner_right + peel_height,
                                y_cursor + 2 * height_in + 2 * peel_height),
                         end=(  x_inner_right,
                                y_cursor + 2 * height_in + 2 * peel_height + flap_height),
                         **cut_args),
                )

        # Bottom
        dwg.add(dwg.line(start=(x_inner_left, y_cursor + side_height),
                         end=(x_inner_right, y_cursor + side_height),
                         **cut_args),
                )

        # 2. Top Face Zone (Red Outline + Cut Wings)
        # Upper Left Side
        dwg.add(dwg.line(start=(x_inner_left, y_cursor),
                         end=(x_inner_left, y_cursor + height_in),
                         **peel_args),
                )
        # Upper Right Side
        dwg.add(dwg.line(start=(x_inner_right, y_cursor),
                         end=(x_inner_right, y_cursor + height_in),
                         **peel_args),
                )
        # Upper Face, Bottom Edge
        dwg.add(dwg.line(start=(x_inner_left, y_cursor + height_in),
                         end=(x_inner_right, y_cursor + height_in),
                         **peel_args),
                )

        y_cursor += height_in + peel_height

        # 2. Bottom Face Zone (Red Outline + Cut Wings)
        dwg.add(dwg.rect(insert=(x_inner_left, y_cursor),
                         size=(inner_w, height_in), **peel_args))
        # bottom left fold
        if folds:
            dwg.add(dwg.line(start=(x_inner_left - peel_height, y_cursor),
                             end=(x_inner_left - peel_height,
                                  y_cursor + height_in + peel_height),
                             **fold_args),
                    )
            # bottom fold
            dwg.add(dwg.line(
                start=(x_inner_left - peel_height, y_cursor + height_in + peel_height),
                end=(x_inner_right + peel_height, y_cursor + height_in + peel_height),
                             **fold_args),
                    )
            # bottom right fold
            dwg.add(dwg.line(start=(x_inner_right + peel_height, y_cursor),
                             end=(x_inner_right + peel_height,
                                  y_cursor + height_in + peel_height),
                             **fold_args),
                    )

        y_cursor += height_in + peel_height

        current_y = y_cursor + flap_height + padding

    # Save
    dwg.save()
    print(f"Template saved to {filename}")

def main():
    parser = argparse.ArgumentParser(
        description="Generate SVG template for a seamless cardboard box.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
    parser.add_argument(
        "--length", '-l',
        type=float,
        default=94,
        help="Interior length (mm) [width of the continuous strip]",
        )
    parser.add_argument(
        "--width", '-w',
        type=float,
        default=90,
        help="Interior width (mm) [Width of the side panels]",
        )
    parser.add_argument(
        "--height", '-H',
        type=float,
        default=38,
        help="Interior height (mm)",
        )
    parser.add_argument(
        "--thickness", '-t',
        type=float,
        default=4,
        help="Cardboard thickness (mm)",
        )
    parser.add_argument(
        '--labels',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Print labels.'
    )
    parser.add_argument(
        '--folds',
        action=argparse.BooleanOptionalAction,
        default=True,
        help='Print folds.'
    )
    parser.add_argument(
        "--fname", '-f',
        type=str,
        default=None,
        help="Output filename (defaults to cbox_[W]_[L]_[H]_[T].svg if not specified)",
    )

    args = parser.parse_args()

    if args.fname is None:
        args.fname = f"cbox_{args.width:0.0f}_{args.length:0.0f}_{args.height:0.0f}_{args.thickness:0.0f}.svg"
    print(f'{args.fname=}')

    create_cbox_template(
        args.length,
        args.width,
        args.height,
        args.thickness,
        args.labels,
        args.folds,
        args.fname
    )

if __name__ == "__main__":
    main()
