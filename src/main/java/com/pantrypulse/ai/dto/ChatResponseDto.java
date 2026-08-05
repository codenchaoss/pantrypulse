package com.pantrypulse.ai.dto;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Data
public class ChatResponseDto {

    private boolean success;
    private String timestamp;
    private ChatDataDto data;
    private String message;

}