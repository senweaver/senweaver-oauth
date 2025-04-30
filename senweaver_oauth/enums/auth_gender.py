"""
用户性别枚举
"""
from enum import Enum
from typing import Optional


class AuthGender(Enum):
    """
    用户性别枚举
    """
    UNKNOWN = 0  # 未知
    MALE = 1     # 男
    FEMALE = 2   # 女
    
    @classmethod
    def get_gender(cls, gender_code: Optional[str]) -> 'AuthGender':
        """
        根据性别代码获取性别枚举
        
        Args:
            gender_code: 性别代码，不同平台可能使用不同的代码
            
        Returns:
            性别枚举
        """
        # 转换为字符串处理
        if gender_code is None:
            return cls.UNKNOWN
            
        gender_str = str(gender_code).lower()
        
        # 处理常见的性别代码
        if gender_str in ('1', 'm', 'male', '男'):
            return cls.MALE
        elif gender_str in ('2', 'f', 'female', '女'):
            return cls.FEMALE
        else:
            return cls.UNKNOWN 