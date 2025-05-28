from datetime import datetime

class DashboardService:
    async def get_dashboard_data(self, user_id: str = ""):
        try:
            current_time = datetime.utcnow()

            # Simulated database calls:
            total_meetings = await self.count_total_meetings()
            attended_meeting_ids = await self.get_attended_meeting_ids(user_id)
            meetings_not_attended = total_meetings - len(attended_meeting_ids)
            upcoming_meeting = await self.get_upcoming_meeting(current_time)
            total_hours_spent = await self.calculate_user_total_hours(user_id)
            total_meeting_hours = await self.calculate_total_meeting_hours()

            return {
                "totalMeetings": total_meetings,
                "meetingsAttended": len(attended_meeting_ids),
                "meetingsNotAttended": meetings_not_attended,
                "upcomingMeeting": upcoming_meeting,
                "totalHoursSpent": f"{total_hours_spent:.2f}",
                "totalMeetingHours": f"{total_meeting_hours:.2f}"
            }
        except Exception as e:
            print(f"Error fetching dashboard data: {e}")
            return { "message": "Internal Server Error" }

    # Dummy placeholder methods (replace with real DB calls)
    async def count_total_meetings(self):
        return 10

    async def get_attended_meeting_ids(self, user_id):
        return ["meeting1", "meeting2"]

    async def get_upcoming_meeting(self, current_time):
        return { "title": "Upcoming Meeting", "start": str(current_time) }

    async def calculate_user_total_hours(self, user_id):
        return 12.5

    async def calculate_total_meeting_hours(self):
        return 45.0
