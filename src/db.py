class UserDatabase:
    """
    Класс для управления данными пользователей.
    В текущей реализации данные хранятся в памяти (для MVP).
    """
    
    def __init__(self):
        """
        Инициализирует пустую базу данных пользователей.
        """
        # Словарь для хранения данных о пользователях
        # user_id: { balance: int }
        self.users = {}
    
    def user_exists(self, user_id):
        """
        Проверяет, существует ли пользователь в базе данных.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            
        Returns:
            bool: True, если пользователь существует, иначе False
        """
        return user_id in self.users
    
    def add_user(self, user_id, initial_balance=1000):
        """
        Добавляет нового пользователя в базу данных.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            initial_balance: Начальный баланс пользователя (по умолчанию 1000)
        """
        if not self.user_exists(user_id):
            self.users[user_id] = {
                "balance": initial_balance
            }
    
    def get_balance(self, user_id):
        """
        Получает текущий баланс пользователя.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            
        Returns:
            int: Текущий баланс пользователя или 0, если пользователь не найден
        """
        if self.user_exists(user_id):
            return self.users[user_id]["balance"]
        return 0
    
    def update_balance(self, user_id, new_balance):
        """
        Обновляет баланс пользователя.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            new_balance: Новое значение баланса
            
        Returns:
            bool: True, если обновление выполнено успешно, иначе False
        """
        if self.user_exists(user_id):
            self.users[user_id]["balance"] = new_balance
            return True
        return False
    
    def add_to_balance(self, user_id, amount):
        """
        Добавляет указанную сумму к балансу пользователя.
        
        Args:
            user_id: Уникальный идентификатор пользователя
            amount: Сумма для добавления (может быть отрицательной)
            
        Returns:
            int: Новый баланс пользователя или None, если пользователь не найден
        """
        if self.user_exists(user_id):
            self.users[user_id]["balance"] += amount
            return self.users[user_id]["balance"]
        return None
