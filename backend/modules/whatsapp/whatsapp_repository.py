from core.database import get_connection


def fetch_pending_notifications(limit: int | None = None):
    """
    Fetch pending notifications.

    If limit is provided -> return at most that many notifications.
    If limit is None -> return all pending notifications.
    """

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            n.notification_id,
            n.report_id,
            p.phone_number AS patient_whatsapp,
            p.name AS patient_name,
            p.patient_id,
            r.lab_id,
            l.lab_name
        FROM dev.patient_notification_details n
        JOIN dev.reports_upload_details r ON n.report_id = r.report_id
        JOIN dev.patients_details p ON r.patient_id = p.patient_id
        JOIN dev.labs_details l ON r.lab_id = l.lab_id
        WHERE n.notification_status_id = 0
        ORDER BY n.processed_at NULLS FIRST, n.retry_count ASC
    """

    if limit:
        query += " LIMIT %s"
        cursor.execute(query, (limit,))
    else:
        cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    notifications = []

    for row in rows:
        notifications.append({
            "notification_id": row[0],
            "report_id": row[1],
            "patient_whatsapp": row[2],
            "patient_name": row[3],
            "patient_id": row[4],
            "lab_id": row[5],
            "lab_name": row[6]
        })

    return notifications


def increment_retry_or_fail(notification_id: str):
    """
    Increment retry count for a notification.
    If retry_count reaches 3, set status to 2 (permanent failure).
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE dev.patient_notification_details
        SET retry_count = retry_count + 1,
            processed_at = NOW()
        WHERE notification_id = %s
        RETURNING retry_count
    """, (notification_id,))

    row = cursor.fetchone()

    if row and row[0] >= 3:
        cursor.execute("""
            UPDATE dev.patient_notification_details
            SET notification_status_id = 2
            WHERE notification_id = %s
        """, (notification_id,))

    conn.commit()

    cursor.close()
    conn.close()


def update_notification_status(notification_id: str, status_id: int, retry_count: int = None):
    """
    Directly set notification status and optionally retry count.
    """

    conn = get_connection()
    cursor = conn.cursor()

    if retry_count is not None:
        cursor.execute("""
            UPDATE dev.patient_notification_details
            SET notification_status_id = %s,
                retry_count = %s,
                processed_at = NOW()
            WHERE notification_id = %s
        """, (status_id, retry_count, notification_id))
    else:
        cursor.execute("""
            UPDATE dev.patient_notification_details
            SET notification_status_id = %s,
                processed_at = NOW()
            WHERE notification_id = %s
        """, (status_id, notification_id))

    conn.commit()

    cursor.close()
    conn.close()