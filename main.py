# main.py
# BOF_CORE – System Initialization Demo (with Logging)

from meta.bof_core import BOFCore
from meta.acf_adapter import ACFAdapter
from meta.ais_surface import AISurface
from core_exec.bpb_core import BPBCore
from core_exec.meth.intent_discovery import IntentDiscovery
from core_exec.meth.rlhf_tuning import RLHFTuning
from data.log.logger import BOFLogger
from core_exec.common_prompts import compose_writing_instruction_payload


def main():
    logger = BOFLogger()
    logger.section("BOF CORE SYSTEM STARTUP")

    print("\n=== Initializing BOF Core System ===\n")

    # Initialize meta-layer modules
    bof = BOFCore()
    acf = ACFAdapter(mode="Standard")
    ais = AISurface()

    # Initialize execution-layer modules
    bpb = BPBCore()
    intent = IntentDiscovery()
    rlhf = RLHFTuning()

    # Attach layers
    bof.attach_acf(acf)
    bof.attach_ais(ais)
    bof.attach_bpb(bpb)

    # Initialize system
    bof.initialize()
    logger.write("BOF initialized successfully.")

    # Simulate data flow
    print("\n=== Simulating Behavioral Cycle ===\n")
    intent.collect_sample("User text vector #1")
    intent.cluster_modes()
    modes = intent.get_modes()
    logger.write(f"Intent discovery completed. Modes: {modes}")
    print("Detected Modes:", modes)

    bpb.run_cycle("Example behavioral data")
    logger.write("Behavioral cycle executed successfully.")

    rlhf.record_feedback("positive")
    rlhf.adjust_parameters()
    logger.write("RLHF tuning cycle completed.")

    logger.section("BOF CORE SYSTEM SHUTDOWN")
    print("\n=== BOF Core System Operational ===\n")


if __name__ == "__main__":
    main()

    # === Adaptive Orchestration Test ===
    from meta.bof_core_adaptive import BOFCoreAdaptive

    def test_adaptive_bof():
        print("\n=== Initializing BOF Adaptive System ===\n")
        acf = ACFAdapter(mode="Standard")
        ais = AISurface()
        bpb = BPBCore()
        intent_detector = IntentDiscovery()

        bof_adaptive = BOFCoreAdaptive(
            acf=acf,
            ais=ais,
            bpb=bpb,
            intent_detector=intent_detector
        )
        bof_adaptive.initialize()
        writing_instruction = compose_writing_instruction_payload()
        bof_adaptive.run(
            intent="writing",
            input_text=writing_instruction
        )
        bof_adaptive.run(
            intent="reading",
            input_text=(
                "Researchers warn that coastal cities may face a tripling of flood events "
                "within the next decade unless new mitigation plans receive funding."
            )
        )

    # Run adaptive version
    test_adaptive_bof()

# original input_text="Explain why adaptive intelligence needs orchestration."
