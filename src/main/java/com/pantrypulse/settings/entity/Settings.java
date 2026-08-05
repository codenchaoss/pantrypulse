package com.pantrypulse.settings.entity;
import com.pantrypulse.authentication.entity.User;
import jakarta.persistence.*;
import lombok.*;
@Entity
@Table(name = "settings")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Settings {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String fullName;

    @Column(nullable = false, unique = true)
    private String email;

    private String phoneNumber;

    private String role;

    private String restaurantName;
    @Lob
    @Column(columnDefinition = "LONGTEXT")
    private String profileImageUrl;

    @Builder.Default
    private Boolean lowStockAlerts = true;

    @Builder.Default
    private Boolean expiryAlerts = true;

    @Builder.Default
    private Boolean aiMenuNotifications = true;

    @Builder.Default
    private Boolean emailNotifications = false;
    
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "owner_id")
    private User owner;
    
}