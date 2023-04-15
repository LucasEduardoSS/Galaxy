def transform(self, x, y):
    """
    Transform the grid layout into 2D or 3D Perspective
    :param x: Starting Vertical Line Point
    :param y: Ending Vertical Line Point
    :return: Execute the transform function
    """
    # return self.transform_2D(x, y)
    return self.transform_perspective(x, y)


def transform_2D(self, x, y):
    return int(x), int(y)


def transform_perspective(self, x, y):
    # "tr_y" is the point in y where the line ends in the perspective view
    lin_y = y * self.perspective_point_y / self.height

    '''
    If the transformed y point be higher than the perspective y point, the transformed y point will receive
    the perspective y point value, limiting it to that point.
    '''
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y

    # Difference between the point x for the treated line and the perspective x point
    diff_x = x - self.perspective_point_x
    # Difference between the transformed y point for the treated line and the perspective y point
    diff_y = self.perspective_point_y - lin_y

    '''
    The "factor_y" will be:
        1 when diff_y == self.perspetive_point_y
        0 when diff_y == 0
    '''
    factor_y = (diff_y / self.perspective_point_y) ** 4

    tr_x = self.perspective_point_x + diff_x * factor_y
    tr_y = self.perspective_point_y - factor_y * self.perspective_point_y

    return int(tr_x), int(tr_y)
