# app/extraction/imap_client.py
import imaplib, email, ssl
from email.header import decode_header
from email.message import Message
from typing import List, Optional


class IMAPClient:
    def __init__(self, host: str, username: str, password: str, port: int = 993):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.conn = None

    def connect(self):
        context = ssl.create_default_context()

        self.conn = imaplib.IMAP4_SSL(self.host, self.port, ssl_context=context)
        self.conn.login(self.username, self.password)
    
    def select_folder(self, folder="INBOX"):
        if self.conn is None:
            raise RuntimeError("Not connected. Call connect() first.")
        self.conn.select(folder)

    def search(self, query: str) -> List[str]:
        if self.conn is None:
            raise RuntimeError("Not connected. Call connect() first.")
        status, data = self.conn.search(None, query)
        if status != "OK":
            return []
        return data[0].decode().split()
    
    def fetch_email(self, uid: str) -> Optional[Message]:
        if self.conn is None:
            raise RuntimeError("IMAP connection not established")
        
        status, data = self.conn.fetch(uid, "(RFC822)")

        if status != "OK" or not data or data[0] is None:
            return None
        
        raw = data[0][1]
        if not isinstance(raw, bytes):
            return None
        return email.message_from_bytes(raw)

    @staticmethod
    def decode(value: Optional[str]) -> str:
        if not value:
            return ""
        decoded, charset = decode_header(value)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(charset or "utf-8", errors="ignore")
        return decoded
    
    @staticmethod
    def extract_html(msg: Message) -> str:
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() ==  "text/html":
                    payload = part.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        return payload.decode("utf-8", errors="ignore")
        else:
            if msg.get_content_type() == "text/html":
                payload = msg.get_payload(decode=True)
                if isinstance(payload, bytes):
                    return payload.decode("utf-8", errors="ignore")
            
        return ""
        