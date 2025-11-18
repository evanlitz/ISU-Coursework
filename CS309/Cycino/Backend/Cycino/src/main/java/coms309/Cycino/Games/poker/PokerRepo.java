package coms309.Cycino.Games.poker;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PokerRepo extends JpaRepository<Poker, Long> {
}
