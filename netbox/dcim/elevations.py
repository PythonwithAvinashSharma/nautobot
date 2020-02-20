import svgwrite

from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode

from utilities.utils import foreground_color
from .choices import DeviceFaceChoices


class RackElevationSVG:
    """
    Use this class to render a rack elevation as an SVG image.
    """
    def __init__(self, rack):
        self.rack = rack

    @staticmethod
    def _add_gradient(drawing, id_, color):
        gradient = drawing.linearGradient(
            start=('0', '0%'),
            end=('0', '5%'),
            spreadMethod='repeat',
            id_=id_,
            gradientTransform='rotate(45, 0, 0)',
            gradientUnits='userSpaceOnUse'
        )
        gradient.add_stop_color(offset='0%', color='#f7f7f7')
        gradient.add_stop_color(offset='50%', color='#f7f7f7')
        gradient.add_stop_color(offset='50%', color=color)
        gradient.add_stop_color(offset='100%', color=color)
        drawing.defs.add(gradient)

    @staticmethod
    def _setup_drawing(width, height):
        drawing = svgwrite.Drawing(size=(width, height))

        # add the stylesheet
        with open('{}/css/rack_elevation.css'.format(settings.STATICFILES_DIRS[0])) as css_file:
            drawing.defs.add(drawing.style(css_file.read()))

        # add gradients
        RackElevationSVG._add_gradient(drawing, 'reserved', '#c7c7ff')
        RackElevationSVG._add_gradient(drawing, 'occupied', '#d7d7d7')
        RackElevationSVG._add_gradient(drawing, 'blocked', '#ffc0c0')

        return drawing

    @staticmethod
    def _draw_device_front(drawing, device, start, end, text):
        name = str(device)
        if device.devicebay_count:
            name += ' ({}/{})'.format(device.get_children().count(), device.devicebay_count)

        color = device.device_role.color
        link = drawing.add(
            drawing.a(
                href=reverse('dcim:device', kwargs={'pk': device.pk}),
                target='_top',
                fill='black'
            )
        )
        link.set_desc('{} — {} ({}U) {} {}'.format(
            device.device_role, device.device_type.display_name,
            device.device_type.u_height, device.asset_tag or '', device.serial or ''
        ))
        link.add(drawing.rect(start, end, style='fill: #{}'.format(color), class_='slot'))
        hex_color = '#{}'.format(foreground_color(color))
        link.add(drawing.text(str(name), insert=text, fill=hex_color))

        # Embed front device type image if one exists
        if device.device_type.front_image:
            url = device.device_type.front_image.url
            image = drawing.image(href=url, insert=start, size=end, class_='device-image')
            image.stretch()
            link.add(image)

    @staticmethod
    def _draw_device_rear(drawing, device, start, end, text):
        rect = drawing.rect(start, end, class_="slot blocked")
        rect.set_desc('{} — {} ({}U) {} {}'.format(
            device.device_role, device.device_type.display_name,
            device.device_type.u_height, device.asset_tag or '', device.serial or ''
        ))
        drawing.add(rect)
        drawing.add(drawing.text(str(device), insert=text))

        # Embed rear device type image if one exists
        if device.device_type.front_image:
            url = device.device_type.rear_image.url
            image = drawing.image(href=url, insert=start, size=end, class_='device-image')
            image.stretch()
            drawing.add(image)

    @staticmethod
    def _draw_empty(drawing, rack, start, end, text, id_, face_id, class_, reservation):
        link = drawing.add(
            drawing.a(
                href='{}?{}'.format(
                    reverse('dcim:device_add'),
                    urlencode({'rack': rack.pk, 'site': rack.site.pk, 'face': face_id, 'position': id_})
                ),
                target='_top'
            )
        )
        if reservation:
            link.set_desc('{} — {} · {}'.format(
                reservation.description, reservation.user, reservation.created
            ))
        link.add(drawing.rect(start, end, class_=class_))
        link.add(drawing.text("add device", insert=text, class_='add-device'))

    def merge_elevations(self, face):
        elevation = self.rack.get_rack_units(face=face, expand_devices=False)
        if face == DeviceFaceChoices.FACE_REAR:
            other_face = DeviceFaceChoices.FACE_FRONT
        else:
            other_face = DeviceFaceChoices.FACE_REAR
        other = self.rack.get_rack_units(face=other_face)

        unit_cursor = 0
        for u in elevation:
            o = other[unit_cursor]
            if not u['device'] and o['device']:
                u['device'] = o['device']
                u['height'] = 1
            unit_cursor += u.get('height', 1)

        return elevation

    def render(self, reserved_units, face, unit_width, unit_height, legend_width):
        """
        Return an SVG document representing a rack elevation.
        """
        drawing = self._setup_drawing(unit_width + legend_width, unit_height * self.rack.u_height)

        unit_cursor = 0
        for ru in range(0, self.rack.u_height):
            start_y = ru * unit_height
            position_coordinates = (legend_width / 2, start_y + unit_height / 2 + 2)
            unit = ru + 1 if self.rack.desc_units else self.rack.u_height - ru
            drawing.add(
                drawing.text(str(unit), position_coordinates, class_="unit")
            )

        for unit in self.merge_elevations(face):

            # Loop through all units in the elevation
            device = unit['device']
            height = unit.get('height', 1)

            # Setup drawing coordinates
            start_y = unit_cursor * unit_height
            end_y = unit_height * height
            start_cordinates = (legend_width, start_y)
            end_cordinates = (legend_width + unit_width, end_y)
            text_cordinates = (legend_width + (unit_width / 2), start_y + end_y / 2)

            # Draw the device
            if device and device.face == face:
                self._draw_device_front(drawing, device, start_cordinates, end_cordinates, text_cordinates)
            elif device and device.device_type.is_full_depth:
                self._draw_device_rear(drawing, device, start_cordinates, end_cordinates, text_cordinates)
            else:
                # Draw shallow devices, reservations, or empty units
                class_ = 'slot'
                reservation = reserved_units.get(unit["id"])
                if device:
                    class_ += ' occupied'
                if reservation:
                    class_ += ' reserved'
                self._draw_empty(
                    drawing,
                    self.rack,
                    start_cordinates,
                    end_cordinates,
                    text_cordinates,
                    unit["id"],
                    face,
                    class_,
                    reservation
                )

            unit_cursor += height

        # Wrap the drawing with a border
        drawing.add(drawing.rect((legend_width, 0), (unit_width, self.rack.u_height * unit_height), class_='rack'))

        return drawing
