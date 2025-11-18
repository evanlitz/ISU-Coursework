package coms309.Cycino.stats;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface UserStatsRepo extends JpaRepository<UserStats, String> {
}
