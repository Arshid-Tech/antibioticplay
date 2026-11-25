import csv
import datetime
from app import create_app
from app.models import User

app = create_app()


def export_users_to_csv():
    with app.app_context():
        print('⏳ در حال دریافت اطلاعات کاربران...')
        users = User.query.all()

        filename = f"users_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.csv"

        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            fieldnames = [
                'نام کاربری',
                'نام',
                'نام خانوادگی',
                'ایمیل',
                'امتیاز کل',
                'سطح (Level)',
                'تعداد آزمون‌های تکمیل شده',
                'تعداد نشان‌ها',
                'جزئیات آزمون‌ها (Quiz Progress)',
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for user in users:
                details = [
                    f"{p.quiz_id}: (نمره: {p.best_score} | تلاش: {p.attempts})"
                    for p in user.quiz_progresses.all()
                ]
                writer.writerow({
                    'نام کاربری': user.username,
                    'نام': user.first_name or '',
                    'نام خانوادگی': user.last_name or '',
                    'ایمیل': user.email,
                    'امتیاز کل': user.score,
                    'سطح (Level)': user.level,
                    'تعداد آزمون‌های تکمیل شده': user.quizzes_completed,
                    'تعداد نشان‌ها': user.earned_badges.count(),
                    'جزئیات آزمون‌ها (Quiz Progress)': ' | '.join(details),
                })

        print(f"✅ اطلاعات {len(users)} کاربر با موفقیت در فایل '{filename}' ذخیره شد.")


if __name__ == '__main__':
    export_users_to_csv()
