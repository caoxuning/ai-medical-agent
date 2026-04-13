"""
数据库模块 - 对话历史持久化存储
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional


class SessionDatabase:
    """
    会话数据库
    存储对话历史、患者信息、会话元数据
    """
    
    def __init__(self, db_path: str = "data/sessions.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表"""
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 会话表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                patient_info TEXT,  -- JSON格式
                status TEXT DEFAULT 'active'  -- active, closed, archived
            )
        ''')
        
        # 消息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,  -- user, assistant, system
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_time ON messages(timestamp)')
        
        conn.commit()
        conn.close()
        print(f"✅ 数据库初始化完成: {self.db_path}")
    
    def save_session(self, session_id: str, patient_info: Dict[str, Any], messages: List[Dict[str, str]]):
        """
        保存会话数据
        
        Args:
            session_id: 会话ID
            patient_info: 患者信息字典
            messages: 消息列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 保存/更新会话
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_id, updated_at, patient_info, status)
                VALUES (?, datetime('now'), ?, 'active')
            ''', (session_id, json.dumps(patient_info, ensure_ascii=False)))
            
            # 只保存新消息（避免重复）
            cursor.execute('SELECT COUNT(*) FROM messages WHERE session_id = ?', (session_id,))
            existing_count = cursor.fetchone()[0]
            
            if len(messages) > existing_count:
                new_messages = messages[existing_count:]
                for msg in new_messages:
                    cursor.execute('''
                        INSERT INTO messages (session_id, role, content, timestamp)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        session_id,
                        msg['role'],
                        msg['content'],
                        msg.get('timestamp', datetime.now().isoformat())
                    ))
            
            conn.commit()
            
        except Exception as e:
            print(f"❌ 保存会话失败: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        加载会话数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            包含 patient_info 和 messages 的字典，或 None
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 加载会话信息
            cursor.execute('''
                SELECT patient_info FROM sessions 
                WHERE session_id = ? AND status = 'active'
            ''', (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            patient_info = json.loads(row[0]) if row[0] else {}
            
            # 加载消息历史
            cursor.execute('''
                SELECT role, content, timestamp FROM messages
                WHERE session_id = ?
                ORDER BY timestamp
            ''', (session_id,))
            
            messages = []
            for role, content, timestamp in cursor.fetchall():
                messages.append({
                    'role': role,
                    'content': content,
                    'timestamp': timestamp
                })
            
            return {
                'session_id': session_id,
                'patient_info': patient_info,
                'messages': messages
            }
            
        except Exception as e:
            print(f"❌ 加载会话失败: {e}")
            return None
        finally:
            conn.close()
    
    def list_sessions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出最近的会话
        
        Args:
            limit: 返回数量限制
            
        Returns:
            会话列表
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT s.session_id, s.created_at, s.updated_at, 
                       COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.session_id = m.session_id
                WHERE s.status = 'active'
                GROUP BY s.session_id
                ORDER BY s.updated_at DESC
                LIMIT ?
            ''', (limit,))
            
            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'created_at': row[1],
                    'updated_at': row[2],
                    'message_count': row[3]
                })
            
            return sessions
            
        except Exception as e:
            print(f"❌ 列出会话失败: {e}")
            return []
        finally:
            conn.close()
    
    def close_session(self, session_id: str):
        """关闭会话（标记为 closed）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE sessions 
                SET status = 'closed', updated_at = datetime('now')
                WHERE session_id = ?
            ''', (session_id,))
            conn.commit()
        except Exception as e:
            print(f"❌ 关闭会话失败: {e}")
        finally:
            conn.close()
    
    def delete_session(self, session_id: str):
        """删除会话"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
            conn.commit()
        except Exception as e:
            print(f"❌ 删除会话失败: {e}")
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT COUNT(*) FROM sessions')
            session_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM messages')
            message_count = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM sessions 
                WHERE status = 'active'
            ''')
            active_count = cursor.fetchone()[0]
            
            return {
                'total_sessions': session_count,
                'active_sessions': active_count,
                'total_messages': message_count
            }
            
        except Exception as e:
            print(f"❌ 获取统计失败: {e}")
            return {}
        finally:
            conn.close()


# 单例
db_instance = None

def get_db() -> SessionDatabase:
    """获取数据库实例"""
    global db_instance
    if db_instance is None:
        db_instance = SessionDatabase()
    return db_instance


if __name__ == "__main__":
    # 测试
    db = SessionDatabase()
    
    # 保存测试数据
    test_session = {
        'session_id': 'test_001',
        'patient_info': {'症状': '头疼', '持续时间': '3天'},
        'messages': [
            {'role': 'user', 'content': '我头疼', 'timestamp': datetime.now().isoformat()},
            {'role': 'assistant', 'content': '请问头疼多久了？', 'timestamp': datetime.now().isoformat()}
        ]
    }
    
    db.save_session(
        test_session['session_id'],
        test_session['patient_info'],
        test_session['messages']
    )
    
    # 加载测试
    loaded = db.load_session('test_001')
    print("加载的会话:", json.dumps(loaded, ensure_ascii=False, indent=2))
    
    # 统计
    stats = db.get_stats()
    print("\n数据库统计:", stats)
