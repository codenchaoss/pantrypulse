package com.pantrypulse.ai.dto;

import lombok.Data;

@Data
public class ChatRequestDto {

    private String question;
    private String history;

}