class BidirectionalIterator:
    """
    RU:
        Базовый класс описывающий разнонаправленный итератор

        Атрибуты:
            self.data: Список каких-либо объектов
            self.index: Индекс элемента из списка
    EN:
        A base class describing a multi-directional iterator

        Attributes:
            self.data: A list of any objects
            self.index: Index of an item from the list
    """
    def __init__(self, data: list):
        self.data = data
        self.index = 0

    def next(self):
        """
        RU:
            Переход к следующему элементу в списке
        EN:
            Move to the next item in the list

        :return: self.data[self.index + 1]
        """
        try:
            self.index += 1
            photo_url = self.data[self.index]
        except IndexError:
            return None
        return photo_url

    def prev(self):
        """
        RU:
            Переход к предыдущему элементу в списке
        EN:
            Move to the previous item in the list

        :return: self.data[self.index - 1]
        """
        self.index -= 1
        photo_url = self.data[self.index]
        if self.index < 0:
            self.index = 0
            return None
        return photo_url
