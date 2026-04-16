from app.repositories.goal_repository import GoalRepository

class GoalService:
  def __init__(self) -> None:
    self.repo = GoalRepository()
    
  def get_progress(self, workspace_id: str, goal_id: str) -> dict | None:
    data = self.repo.get_goal_progress(workspace_id, goal_id)
    if not data:
      raise ValueError("Goal not found")
    
    target_cents = int(data["target_amount_cents"] or 0)
    current_cents = int(data["current_amount_cents"] or 0)
    
    progress_percent = (current_cents / target_cents * 100) if target_cents > 0 else 0.0
    progress_percent = round(progress_percent, 2)
    
    remaining_cents = max(target_cents - current_cents, 0)
    is_completed = current_cents >= target_cents

    return {
      **data,
      "progress_percent": progress_percent,
      "remaining_amount_cents": remaining_cents,
      "is_completed": is_completed
    }