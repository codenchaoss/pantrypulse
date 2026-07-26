package com.pantrypulse.historicalorder.entity;

import com.pantrypulse.recipe.entity.Recipe;
import jakarta.persistence.*;
import lombok.*;
import com.pantrypulse.authentication.entity.User;
import java.time.LocalDate;

@Entity
@Table(name = "historical_orders")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class HistoricalOrder {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "recipe_id", nullable = false)
    private Recipe recipe;

    @Column(nullable = false)
    private Integer quantity;

    @Column(nullable = false)
    private LocalDate orderDate;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "owner_id")
    private User owner;
}